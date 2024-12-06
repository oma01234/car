# utils.py or wherever appropriate
import secrets
import hashlib
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_verification_token():
    token = secrets.token_urlsafe(16)
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def send_verification_email(user):
    token = generate_verification_token()
    user.profile.verification_token = token  # Assuming profile has a OneToOneField with User
    user.profile.save()

    subject = 'Verify your email address'
    html_message = render_to_string('verification_email.html', {'token': token})
    plain_message = strip_tags(html_message)

    send_mail(subject, plain_message, 'from@example.com', [user.email], html_message=html_message)