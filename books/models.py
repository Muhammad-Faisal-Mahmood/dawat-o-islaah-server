import os
import shutil
import subprocess
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    title = models.CharField(_('title'), max_length=200)
    author = models.CharField(_('author'), max_length=100, blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)

    pdf_file = models.FileField(_('PDF file'), upload_to='books/pdfs/')
    cover_image = models.ImageField(_('cover image'), upload_to='books/covers/', blank=True, null=True)

    # ✅ NEW FIELDS
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('pdf', 'PDF'),
            ('ocr', 'OCR'),
            ('html', 'HTML'),
        ],
        default='pdf'
    )

    extracted_text = models.TextField(blank=True, null=True)
    html_content = models.TextField(blank=True, null=True)

    total_pages = models.PositiveIntegerField(_('total pages'), default=0)
    is_split = models.BooleanField(_('pages split'), default=False)

    read_count = models.PositiveIntegerField(_('read count'), default=0)
    download_count = models.PositiveIntegerField(_('download count'), default=0)

    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    is_public = models.BooleanField(_('is public'), default=True)

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')
        ordering = ('-uploaded_at',)

    def __str__(self):
        return self.title

    @property
    def pages_dir(self):
        return os.path.join(
            os.path.dirname(self.pdf_file.path),
            '..', 'pages', str(self.pk)
        )

    @property
    def pages_url_prefix(self):
        return f'/media/books/pages/{self.pk}/'

    # =========================================================
    # 🔍 CHECK IF PDF HAS REAL TEXT (UNICODE DETECTION)
    # =========================================================
    def _has_text(self, pdf_path):
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            for page in doc:
                if page.get_text().strip():
                    return True
            return False
        except Exception as e:
            print(f"Text detection failed: {e}")
            return True  # fallback (assume text exists)

    # =========================================================
    # 🤖 OCR FOR SCANNED PDFs
    # =========================================================
    def _run_ocr(self, pdf_path):
        try:
            output_path = pdf_path.replace(".pdf", "_ocr.pdf")

            subprocess.run(
                ['tesseract', pdf_path, output_path.replace(".pdf", ""), '-l', 'eng+urd', 'pdf'],
                check=True
            )

            if os.path.exists(output_path):
                os.replace(output_path, pdf_path)

            print(f"✅ OCR completed for {self.title}")
            return True
        except Exception as e:
            print(f"OCR failed: {e}")
            return False

    # =========================================================
    # 💾 SAVE METHOD (no blocking processing call)
    # =========================================================
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    # =========================================================
    # ✂️ SPLIT PDF + RENDER PAGE IMAGES (parallelized)
    # =========================================================
    def _split_pdf(self):
        import fitz
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import os

        input_path = self.pdf_file.path
        if not input_path.lower().endswith('.pdf'):
            return

        try:
            doc = fitz.open(input_path)
        except Exception as e:
            print(f"Could not open PDF for {self.title}: {e}")
            return

        total_pages = doc.page_count
        doc.close()

        pages_dir = os.path.normpath(self.pages_dir)
        if os.path.exists(pages_dir):
            shutil.rmtree(pages_dir)
        os.makedirs(pages_dir, exist_ok=True)

        def _save_page(i):
            page_num = i + 1
            src = fitz.open(input_path)
            page = src[i]

            page_pdf_path = os.path.join(pages_dir, f'page-{page_num}.pdf')
            single = fitz.open()
            single.insert_pdf(src, from_page=i, to_page=i)
            single.save(page_pdf_path, garbage=4, deflate=True)
            single.close()

            img_path = os.path.join(pages_dir, f'page-{page_num}.jpg')
            try:
                pix = page.get_pixmap(dpi=150)
                pix.save(img_path)
            except Exception as e:
                print(f"Failed to render page {page_num} image for {self.title}: {e}")

            src.close()

        workers = min(os.cpu_count() or 2, 8)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_save_page, i) for i in range(total_pages)]
            for future in as_completed(futures):
                future.result()

        Book.objects.filter(pk=self.pk).update(
            total_pages=total_pages,
            is_split=True
        )

        self.total_pages = total_pages
        self.is_split = True

        print(f"Split '{self.title}' into {total_pages} pages")

    # =========================================================
    # Re-render page images from already-split page PDFs
    # =========================================================
    def render_page_images(self):
        pages_dir = os.path.normpath(self.pages_dir)
        if not os.path.exists(pages_dir):
            print(f"No split pages found for {self.title}, run _split_pdf first")
            return
        import fitz
        for i in range(1, self.total_pages + 1):
            img_path = os.path.join(pages_dir, f'page-{i}.jpg')
            if os.path.exists(img_path):
                continue
            page_pdf = os.path.join(pages_dir, f'page-{i}.pdf')
            if not os.path.exists(page_pdf):
                continue
            try:
                doc = fitz.open(page_pdf)
                page = doc[0]
                pix = page.get_pixmap(dpi=150)
                pix.save(img_path)
                doc.close()
            except Exception as e:
                print(f"Failed to render page {i} image for {self.title}: {e}")

    # =========================================================
    def delete(self, *args, **kwargs):
        pages_dir = os.path.normpath(self.pages_dir)
        if os.path.exists(pages_dir):
            shutil.rmtree(pages_dir)
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('book_detail', args=[str(self.id)])


class UserBookRead(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_reads')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='read_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_book_reads'
        unique_together = ('user', 'book')


class UserBookDownload(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_downloads')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='download_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_book_downloads'
        unique_together = ('user', 'book')


class BookSessionRead(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='session_reads')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'book_session_reads'
        unique_together = ('session_key', 'book')


class BookSessionDownload(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='session_downloads')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'book_session_downloads'
        unique_together = ('session_key', 'book')
