from celery import shared_task
from django.core.mail import EmailMessage

@shared_task
def send_bill_email(to_email, subject, message, attachment_path):
    email = EmailMessage(
        subject,
        message,
        from_email=None,  # uses EMAIL_HOST_USER from settings.py
        to=[to_email]
    )
    email.attach_file(attachment_path)
    email.send(fail_silently=False)
    return f"Email sent to {to_email}"