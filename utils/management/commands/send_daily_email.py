from django.core.management.base import BaseCommand
from utils.send_daily_email import send_daily_ayat_hadith


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        send_daily_ayat_hadith()

        self.stdout.write("Daily Ayat & Hadith emails sent")