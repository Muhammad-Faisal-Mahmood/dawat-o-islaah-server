import requests
import time
from django.core.management.base import BaseCommand
from hadith.models import Hadith, Book

API_KEY = "$2y$10$d4nL2E660zHHBrwTB7Bviu3WvW5sToLRBWFbJ1yhn7rJzSuNpA0S"
BASE_URL = "https://hadithapi.com/api/hadiths"

class Command(BaseCommand):
    help = "Repairs chapter numbers and resets internal chapter hadith numbering"

    def handle(self, *args, **kwargs):
        books = Book.objects.all()

        for book in books:
            self.stdout.write(self.style.MIGRATE_LABEL(f"Repairing: {book.name}"))
            page = 1

            while True:
                params = {"apiKey": API_KEY, "book": book.name, "page": page}
                success = False

                for attempt in range(3):  # Retry 3 times
                    try:
                        # Increased timeout to 60 to prevent the Read timed out errors
                        response = requests.get(BASE_URL, params=params, timeout=60)
                        if response.status_code == 200:
                            success = True
                            break
                        elif response.status_code == 404:
                            break
                    except requests.exceptions.RequestException:
                        self.stdout.write(f"  Retrying page {page} (Attempt {attempt+1}/3)...")
                        time.sleep(3)

                if not success:
                    self.stdout.write(self.style.WARNING(f"  Skipping page {page} for {book.name} after failures."))
                    break

                data = response.json()
                hadith_list = data.get("hadiths", {}).get("data", [])

                if not hadith_list:
                    break

                for item in hadith_list:
                    try:
                        # 1. Clean Global Hadith Number
                        raw_number = item.get("hadithNumber")
                        if isinstance(raw_number, str) and "," in raw_number:
                            raw_number = raw_number.split(",")[0].strip()
                        h_num = int(raw_number)

                        # 2. Get Chapter Number and Urdu Name
                        chapter_data = item.get("chapter", {})
                        c_num = chapter_data.get("chapterNumber") if isinstance(chapter_data, dict) else 0
                        c_urdu = chapter_data.get("chapterUrdu", "") if isinstance(chapter_data, dict) else ""

                        # 3. Get Internal Chapter Number (The 0, 1, 2... sequence)
                        # The API provides this as 'hadithNumberInChapter'
                        h_in_chapter = item.get("hadithNumberInChapter", 0)

                        # Update database
                        Hadith.objects.filter(book=book, hadith_number=h_num).update(
                            chapter_number=c_num,
                            chapter_urdu=c_urdu,
                            # MAKE SURE 'chapter_hadith_id' MATCHES YOUR MODEL FIELD NAME
                            chapter_hadith_id=h_in_chapter 
                        )
                    except Exception as e:
                        continue

                self.stdout.write(f"  ✅ Page {page} synced (Chapter Hadith IDs updated)")
                page += 1
                # Slightly longer sleep to avoid hitting API rate limits
                time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS("Repair finished! All chapters and internal numbers updated."))
