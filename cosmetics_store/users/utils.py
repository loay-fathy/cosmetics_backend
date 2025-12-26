# utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .tokens import account_activation_token

def send_activation_email(user):
    """
    Sends the activation email to the user.
    """
    subject = 'Activate Your Account'
    
    # Generate token and user ID
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    
    # This is your Next.js frontend URL
    # We'll need to add FRONTEND_URL to settings.py
    activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"

    message = f'Hi {user.username},\n\nPlease click the link below to activate your account:\n\n{activation_link}'
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )