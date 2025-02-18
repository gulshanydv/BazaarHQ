#utils.py

import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from twilio.rest import Client


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def send_otp_mail(email):
    otp = generate_otp()
    # Store OTP in cache with a minute timeout
    cache.set(f'otp_{email}', otp, timeout=60*2)

    subject = 'Your OTP for Signup'
    message = f'Your OTP is {otp}. It will expires within a minute.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    return otp


def send_sms(to_phone_number, message):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_phone_number = settings.TWILIO_PHONE_NUMBER

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            to=to_phone_number,
            from_=from_phone_number,
            body=message,
        )
        print(f"Message sent: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

