from django.core.management.base import BaseCommand
from hadith.models import Book, Hadith

class Command(BaseCommand):
    help = 'Fixes the chapter_hadith_id sequencing for all books'

    def handle(self, *args, **options):
        self.stdout.write("--- STARTING SEQUENCING REPAIR ---")
        
        for book in Book.objects.all():
            self.stdout.write(f"Processing {book.name}...")
            
            # Get unique chapters in order
            chapters = (
                Hadith.objects.filter(book=book)
                .values_list('chapter_number', flat=True)
                .distinct()
                .order_by('chapter_number')
            )
            
            for ch_num in chapters:
                # Get hadiths in this chapter ordered by their global number
                hadiths = Hadith.objects.filter(
                    book=book, 
                    chapter_number=ch_num
                ).order_by('hadith_number')
                
                counter = 1
                for h in hadiths:
                    # Only update if the number is actually different to save DB hits
                    if h.chapter_hadith_id != counter:
                        h.chapter_hadith_id = counter
                        h.save(update_fields=['chapter_hadith_id'])
                    counter += 1
            
            self.stdout.write(self.style.SUCCESS(f"Finished {book.name}"))
            
        self.stdout.write(self.style.SUCCESS("--- ALL BOOKS REPAIRED ---"))
