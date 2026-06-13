import threading
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.html import strip_tags
from .models import User

def send_welcome_email(subject, html_message, email_from, recipient_list):
    """
    Sends an HTML email using Django's EmailMessage.
    """
    with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
    ) as connection:
        # Create plain text version for email clients that don't support HTML
        plain_message = strip_tags(html_message)
        
        # Create EmailMessage with HTML content
        email = EmailMessage(
            subject,
            plain_message,  # Plain text version
            email_from,
            recipient_list,
            connection=connection
        )
        email.content_subtype = "html"  # Set content type to HTML
        email.body = html_message  # Add HTML content
        email.send()

@receiver(post_save, sender=User)
def send_mail_to_reporter(sender, instance, created, **kwargs):
    if created:
        subject = 'Welcome to Dawat-e-Islah - Your Islamic Guidance Platform'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]
        
        # HTML email template
        html_message = f'''
        <html>
        <head>
            <style>
            
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    background-color: #2c5f2d;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                }}
                .footer {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    text-align: center;
                    font-size: 0.9em;
                }}
                .highlight {{
                    color: #2c5f2d;
                    font-weight: bold;
                }}
                .btn {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 20px 0;
                    background-color: #2c5f2d;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Assalamu Alaikum wa Rahmatullahi wa Barakatuh, {instance.first_name}!</h1>
            </div>
            
            <div class="content">
                <p>We are honored to welcome you to <span class="highlight">Dawat-e-Islah</span> - Your Gateway to Authentic Islamic Solutions 🌙</p>
                
                <p>Your journey towards seeking Islamic knowledge begins today. Here's what we offer:</p>
                
                <ul>
                    <li>📖 Reliable answers to your Islamic questions</li>
                    <li>🕌 Guidance based on Quran and Sunnah</li>
                    <li>🤝 Connection with authentic Islamic resources</li>
                    <li>💡 Solutions for contemporary issues</li>
                </ul>
                
                <p>Our team of scholars is ready to assist you with:</p>
                <ul>
                    <li>✅ Matters of Aqeedah (Islamic creed)</li>
                    <li>✅ Fiqh (Islamic jurisprudence)</li>
                    <li>✅ Spiritual guidance</li>
                    <li>✅ Contemporary Islamic issues</li>
                </ul>
                
                <p>Remember the words of our Prophet ﷺ:</p>
                <blockquote style="background: #f4f4f4; padding: 10px; border-left: 5px solid #2c5f2d;">
                    "Seeking knowledge is an obligation upon every Muslim." (Ibn Majah)
                </blockquote>
                
                <p>Need assistance? Reach out to us at <a href="mailto:support@dawateislah.com">support@dawateislah.com</a></p>
                
                <a style="color: white;" href="https://www.dawateislah.com" class="btn">Visit Our Website</a>
            </div>
            
            <div class="footer">
                <p>Jazakum Allah Khairan for choosing Dawat-e-Islah!</p>
                <p>Wasalam,<br>The Dawat-e-Islah Team</p>
            </div>
        </body>
        </html>
        '''

        email_thread = threading.Thread(
            target=send_welcome_email,
            args=(subject, html_message, email_from, recipient_list)
        )
        email_thread.start()