import json
import datetime
import os
from django.conf import settings

BASE_DIR = settings.BASE_DIR

VERSE_FILE = os.path.join(BASE_DIR, "utils/daily_content/dailyVerse.json")
HADITH_FILE = os.path.join(BASE_DIR, "utils/daily_content/dailyHadith.json")


def get_daily_content():

    with open(VERSE_FILE, encoding="utf-8") as f:
        verses = json.load(f)

    with open(HADITH_FILE, encoding="utf-8") as f:
        hadiths = json.load(f)

    day = datetime.datetime.now().day

    verse_index = (day - 1) % len(verses)
    hadith_index = (day - 1) % len(hadiths)

    return verses[verse_index], hadiths[hadith_index]