from django.core.management.base import BaseCommand
from books.models import Book


class Command(BaseCommand):
    help = 'Split all existing books into individual pages'

    def handle(self, *args, **options):
        books = Book.objects.filter(is_split=False)
        self.stdout.write(f"Found {books.count()} books to split...")

        for book in books:
            if book.pdf_file and book.pdf_file.path:
                self.stdout.write(f"Splitting: {book.title}...")
                try:
                    book._split_pdf()
                    self.stdout.write(self.style.SUCCESS(
                        f"  ✅ {book.title} → {book.total_pages} pages"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"  ❌ {book.title}: {e}"
                    ))

        self.stdout.write(self.style.SUCCESS("Done!"))
