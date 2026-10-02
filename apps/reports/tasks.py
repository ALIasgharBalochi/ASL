import os

from celery import shared_task
from django.core.mail import send_mail

from .services import (
    get_report_period_times,
    get_period_reporting,
)


@shared_task
def generate_periodic_report(period):
    start, end = get_report_period_times(period)
    report = get_period_reporting(start, end)

    subject = f"{period.capitalize()} Report"

    message = (
        f"Report period:\n"
        f"From: {start}\n"
        f"To: {end}\n\n"
        f"Forms: {report['form_count']}\n"
        f"Total views: {report['total_view']}\n"
        f"Total submissions: {report['total_submissions']}\n"
    )

    recipient = os.getenv("REPORT_EMAIL_TO")

    if not recipient:
        raise ValueError("REPORT_EMAIL_TO is not configured")

    send_mail(
        subject,
        message,
        os.getenv("EMAIL_HOST_USER"),
        [recipient],
    )

    return report