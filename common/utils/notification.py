from django.core.mail import send_mail
import os


def send_email(email, message: str, subject):
    sending_code = send_mail(
        subject=subject,
        message=message,
        from_email="alibalochi@gmail.com",
        recipient_list=[email],
    )

    return sending_code
