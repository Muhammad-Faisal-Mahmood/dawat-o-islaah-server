from django.core.management.base import BaseCommand
from hadith.models import Hadith, Chapter, Book


class Command(BaseCommand):
    help = "Populate Chapter model from distinct Hadith chapter data"

    def handle(self, *args, **options):
        books = Book.objects.all()
        total_created = 0

        for book in books:
            hadiths = (
                Hadith.objects.filter(book=book)
                .order_by("chapter_number")
                .values(
                    "chapter_number",
                    "chapter_english",
                    "chapter_arabic",
                    "chapter_urdu",
                )
                .distinct()
            )

            seen_numbers = set()
            for h in hadiths:
                num = h["chapter_number"]
                if num in seen_numbers:
                    continue
                seen_numbers.add(num)

                chapter, created = Chapter.objects.get_or_create(
                    book=book,
                    chapter_number=num,
                    defaults={
                        "chapter_english": h["chapter_english"] or "",
                        "chapter_arabic": h["chapter_arabic"] or "",
                        "chapter_urdu": h["chapter_urdu"] or "",
                    },
                )
                if created:
                    total_created += 1
                    self.stdout.write(f"  Created: {chapter}")

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created {total_created} chapters.")
        )
