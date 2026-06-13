import os
from celery import shared_task


def _process_book_pdf_sync(book_id):
    from .models import Book

    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return

    pdf_path = book.pdf_file.path
    if not pdf_path.lower().endswith('.pdf') or not os.path.exists(pdf_path):
        return

    has_text = book._has_text(pdf_path)

    if not has_text:
        success = book._run_ocr(pdf_path)
        content_type = 'ocr' if success else 'pdf'
    else:
        content_type = 'pdf'

    book._split_pdf()

    Book.objects.filter(pk=book_id).update(
        content_type=content_type,
    )
    print(f"Done processing book '{book.title}' (ID={book_id})")


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def process_book_pdf(self, book_id):
    _process_book_pdf_sync(book_id)
