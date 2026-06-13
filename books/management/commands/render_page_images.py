from django.core.management.base import BaseCommand
from books.models import Book


class Command(BaseCommand):
    help = 'Render page images for all split books (for instant front-end display)'

    def handle(self, *args, **options):
        books = Book.objects.filter(is_split=True)
        self.stdout.write(f"Found {books.count()} split books...")

        for book in books:
            if book.pdf_file and book.pdf_file.path:
                self.stdout.write(f"Rendering images: {book.title}...")
                try:
                    book.render_page_images()
                    self.stdout.write(self.style.SUCCESS(
                        f"  ✅ {book.title} ({book.total_pages} pages)"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"  ❌ {book.title}: {e}"
                    ))

        self.stdout.write(self.style.SUCCESS("Done!"))
