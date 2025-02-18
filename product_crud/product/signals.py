from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check if the user already has a UserProfile before creating one
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance)
    else:
        # Update the profile if it exists
        instance.userprofile.save()



@receiver(user_logged_in)
def send_login_notification(sender, request, user, **kwargs):
    print(f'User {user.username} logged in from IP: {request.META.get("REMOTE_ADDR")}')
    print(f'User last login: {user.last_login}')
    
    # Check if the user has logged in from a new device or location
    if user.last_login != request.user.last_login:
        print(f"Sending email notification to {user.email}...")
        send_mail(
            'New Login Detected',
            'Hello {},\n\nA new login was detected to your account at {}\n\nIf this wasn’t you, please reset your password immediately.'.format(user.username, request.META.get('REMOTE_ADDR')),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    else:
        print("No email sent, last login is the same.")
