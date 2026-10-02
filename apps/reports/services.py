from django.db.models import Count, Sum, Avg, Min, Max, FloatField, Q
from django.db.models.functions import Cast
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from ..forms.models import Form, Answer, Submission
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def get_form_report(form):

    questions = form.questions.all()

    report = []

    for question in questions:

        if question.type == "number":

            answers = question.answers.all()

            values = []

            answers = question.answers.annotate(
                numeric_value=Cast("value", FloatField())
            )

            statistics = answers.aggregate(
                count=Count("id"),
                sum=Sum("numeric_value"),
                average=Avg("numeric_value"),
                min=Min("numeric_value"),
                max=Max("numeric_value"),
            )

            report.append(
                {
                    "question": question.text,
                    "type": question.type,
                    "statistics": statistics,
                }
            )

        elif question.type in ["select", "checkbox"]:

            options = question.options.annotate(answer_count=Count("answers"))

            options_report = []

            for option in options:

                count = option.answers.count()

                options_report.append(
                    {
                        "id": option.id,
                        "value": option.value,
                        "count": count,
                    }
                )

            report.append(
                {
                    "question": question.text,
                    "type": question.type,
                    "options": options_report,
                }
            )

    return report


from dateutil.relativedelta import relativedelta
from django.utils import timezone


def get_report_period_times(period):
    now = timezone.now()

    minute = (now.minute // 5) * 5

    now = now.replace(
        minute=minute,
        second=0,
        microsecond=0,
    )

    if period == "weekly":
        start = now - relativedelta(weeks=1)

    elif period == "monthly":
        start = now - relativedelta(months=1)

    else:
        raise ValueError("Invalid report period")

    return start, now


def get_period_reporting(start, end):
    forms = Form.objects.filter(
        created_at__gte=start,
        created_at__lt=end,
    )

    form_count = forms.count()

    total_view = forms.aggregate(total_view=Sum("views"))

    total_submissions = Submission.objects.filter(
        created_at__gte=start,
        created_at__lt=end,
    ).count()

    return {
        "form_count": form_count,
        "total_view": total_view["total_view"] or 0,
        "total_submissions": total_submissions,
    }


def get_reporting_realtime_form(form_id):
    total_submissions = Submission.objects.filter(form__id=form_id).count() or 0
    total_view = Form.objects.get(id=form_id).views or 0
    return {
        "total_submissions": total_submissions,
        "total_views": total_view,
    }


def send_report_update(form_id):
    channel_layer = get_channel_layer()
    data = get_reporting_realtime_form(form_id)

    async_to_sync(channel_layer.group_send)(
        f"form_report_{form_id}",
        {
            "type": "report.update",
            "data": data,
        },
    )
