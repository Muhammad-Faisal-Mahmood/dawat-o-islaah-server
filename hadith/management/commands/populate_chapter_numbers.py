# hadith/management/commands/populate_chapter_numbers.py

from django.core.management.base import BaseCommand
from hadith.models import Hadith, Book


class Command(BaseCommand):
    help = "Populate chapter_number for all hadiths based on first-appearance order within each book"

    def handle(self, *args, **options):
        books = Book.objects.all().order_by('order')

        for book in books:
            self.stdout.write(f"\n📖 Processing: {book.name}")

            # Get all hadiths for this book ordered by hadith_number
            # This preserves the ORIGINAL order from the source
            hadiths = Hadith.objects.filter(book=book).order_by('hadith_number')

            seen_chapters = {}  # chapter_english -> chapter_number
            chapter_counter = 0
            updated_count = 0

            for h in hadiths:
                chapter_key = h.chapter_english.strip()

                if chapter_key not in seen_chapters:
                    chapter_counter += 1
                    seen_chapters[chapter_key] = chapter_counter
                    self.stdout.write(
                        f"  Chapter {chapter_counter}: {chapter_key}"
                    )

                assigned_number = seen_chapters[chapter_key]

                if h.chapter_number != assigned_number:
                    h.chapter_number = assigned_number
                    h.save(update_fields=['chapter_number'])
                    updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✅ {book.name}: {chapter_counter} chapters, "
                    f"{updated_count} hadiths updated"
                )
            )

        self.stdout.write(self.style.SUCCESS("\n🎉 All done!"))
