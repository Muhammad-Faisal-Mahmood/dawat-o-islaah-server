import re
import threading
from dawat_o_islaah.settings import *
from django.core.mail import send_mail

def validate_password(password):
    special_characters = r'[!@#$%^&*()\-_=+{}\[\]|;:"<>,.?/]'
    special_characters_count = len(re.findall(special_characters, password))

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if special_characters_count < 1:
        raise ValueError("Password must contain at least 1 special character.")


def send_forget_password_email(first_name, email, absurl):
    subject = 'Forgot your password?'
    message = f'''Dear {first_name},

    Please click on the link to reset your password: {absurl}

    '''
    from_email = EMAIL_HOST_USER
    recipient_list = [email]

    email_thread = threading.Thread(target=send_mail, args=(subject, message, from_email, recipient_list))
    email_thread.start()