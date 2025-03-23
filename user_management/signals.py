from .models import *
import threading

from dawat_o_islaah.settings import * 

from django.core.mail import EmailMessage, get_connection
from django.dispatch import receiver
from django.db.models.signals import post_save


def send_welcome_email(subject, message, email_from, recipient_list):
    with get_connection(
            host=EMAIL_HOST,
            port=EMAIL_PORT,
            username=EMAIL_HOST_USER,
            password=EMAIL_HOST_PASSWORD,
            use_tls=EMAIL_USE_TLS
    ) as connection:
        email = EmailMessage(subject, message, email_from, recipient_list, connection=connection)
        email.send()

@receiver(post_save, sender=User)
def send_mail_to_repoter(sender, instance, created, **kwargs):
    if created:
        
        subject = 'Welcome to Family'
        email_from = EMAIL_HOST_USER
        recipient_list = [instance.email]
        message = f'''
                Assalamu Alaikum wa Rahmatullahi wa Barakatuh, {instance.first_name}!

                Welcome to Dawat-e-Islah - Your Gateway to Islamic Solutions 🌙

                We are honored to have you join our community of seekers of Islamic knowledge. Your journey towards finding authentic Islamic guidance begins today.

                At Dawat-e-Islah, we are committed to:
                - Providing reliable answers to your daily Islamic questions
                - Offering solutions based on Quran and Sunnah
                - Connecting you with authentic Islamic resources
                - Helping resolve contemporary issues through classical Islamic wisdom

                Our team of knowledgeable scholars and researchers is always ready to assist you with:
                ✓ Matters of Aqeedah (Islamic creed)
                ✓ Fiqh (Islamic jurisprudence) questions
                ✓ Spiritual guidance and self-improvement
                ✓ Contemporary Islamic issues

                May Allah SWT bless your journey of seeking knowledge. Remember the words of our Prophet ﷺ:
                "Seeking knowledge is an obligation upon every Muslim." (Ibn Majah)

                If you have any questions or need assistance, please don't hesitate to reach out to us at [Your Contact Email]. We're here to help you grow in your Deen.

                Jazakum Allah Khairan for choosing Dawat-e-Islah as your trusted Islamic resource.

                Wasalam,
                The Dawat-e-Islah Team
        '''

        # Create a new thread to send the email in the background
        email_thread = threading.Thread(
            target=send_welcome_email,
            args=(subject, message, email_from, recipient_list)
        )
        email_thread.start()