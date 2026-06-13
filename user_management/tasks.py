import logging
from datetime import datetime, date, timedelta
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from prayer_times_calculator import PrayerTimesCalculator

logger = logging.getLogger(__name__)

@shared_task
def send_individual_fajr_email(user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Add your Ayat/Hadith logic here later
        subject = "Dawat-o-Islaah: Your Daily Fajr Inspiration"
        message = f"Assalamu Alaikum {user.first_name},\n\nIt is almost Fajr time in your location. Here is your daily Ayat and Hadith..."
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"SUCCESS: Fajr email sent to {user.email}")
    except Exception as e:
        logger.error(f"FAILED to send email to {user_id}: {str(e)}")

@shared_task
def dispatch_fajr_emails():
    """
    This task runs hourly. It finds users who need an email 
    and schedules their individual delivery time.
    """
    users = User.objects.filter(
        receive_daily_email=True, 
        latitude__isnull=False, 
        longitude__isnull=False
    )
    
    now = datetime.now()
    
    for user in users:
        try:
            # 1. Calculate Fajr using the successful method from our shell test
            calc = PrayerTimesCalculator(
                latitude=float(user.latitude),
                longitude=float(user.longitude),
                calculation_method='isna',
                date=str(date.today()),
                school='hanafi'
            )
            times = calc.fetch_prayer_times()
            fajr_str = times['Fajr'] # e.g., "05:10"
            
            # 2. Convert "05:10" into a real datetime for today
            fajr_hour, fajr_minute = map(int, fajr_str.split(':'))
            local_fajr = now.replace(hour=fajr_hour, minute=fajr_minute, second=0, microsecond=0)
            
            # 3. Logic: If 05:10 has already passed today, schedule for tomorrow
            if local_fajr < now:
                local_fajr += timedelta(days=1)

            # 4. Schedule the task with ETA (Estimated Time of Arrival)
            # This tells Celery: "Hold this email until exactly local_fajr"
            send_individual_fajr_email.apply_async((user.id,), eta=local_fajr)
            
            logger.info(f"SCHEDULED: Email for {user.email} at {local_fajr}")
            
        except Exception as e:
            logger.error(f"SCHEDULING ERROR for {user.email}: {str(e)}")