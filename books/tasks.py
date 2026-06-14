import os
from celery import shared_task
from django.db.models import F


def _process_book_pdf_sync(book_id):
    from .models import Book

    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return

    pdf_path = book.pdf_file.path
    if not pdf_path.lower().endswith('.pdf') or not os.path.exists(pdf_path):
        Book.objects.filter(pk=book_id).update(processing_status='failed')
        return

    try:
        Book.objects.filter(pk=book_id).update(processing_status='processing')

        # Fast pre-render all pages at 72 DPI so frontend has images instantly
        book.render_lowres_page_images()

        book._split_pdf()

        # Determine content type after split (check first page for text)
        try:
            import fitz
            pdoc = fitz.open(book.pages_dir + '/page-1.pdf')
            has_text = len(pdoc[0].get_text().strip()) > 0
            pdoc.close()
            content_type = 'pdf' if has_text else 'ocr'
        except Exception:
            content_type = 'pdf'

        Book.objects.filter(pk=book_id).update(
            content_type=content_type,
            processing_status='completed',
        )
        print(f"Done processing book '{book.title}' (ID={book_id})")
    except Exception as e:
        print(f"Failed processing book '{book.title}' (ID={book_id}): {e}")
        Book.objects.filter(pk=book_id).update(processing_status='failed')


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def process_book_pdf(self, book_id):
    _process_book_pdf_sync(book_id)
