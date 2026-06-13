from django.core.management.base import BaseCommand
from django.db.models import F
from hadith.models import Book, Hadith

OFFSET = 1_000_000

class Command(BaseCommand):
    help = 'Fixes global hadith numbering to start from 1 for sahih-muslim and mishkat'

    def handle(self, *args, **options):
        fixes = {
            'sahih-muslim': +1,
            'mishkat': -1,
        }

        for book_name, shift in fixes.items():
            book = Book.objects.get(name=book_name)

            hadiths = Hadith.objects.filter(book=book)
            count = hadiths.count()
            old_min = hadiths.aggregate(m=__import__('django').db.models.Min('hadith_number'))['m']
            old_max = hadiths.aggregate(m=__import__('django').db.models.Max('hadith_number'))['m']
            self.stdout.write(f"{book_name}: {count} hadiths, range {old_min}-{old_max}")

            hadiths.update(hadith_number=F('hadith_number') + OFFSET)

            hadiths.update(hadith_number=F('hadith_number') - (OFFSET - shift))

            new_min = hadiths.aggregate(m=__import__('django').db.models.Min('hadith_number'))['m']
            new_max = hadiths.aggregate(m=__import__('django').db.models.Max('hadith_number'))['m']
            self.stdout.write(self.style.SUCCESS(
                f"  -> new range {new_min}-{new_max} (shifted by {shift:+d})"
            ))
