from django.db.models import Count, Sum, Avg, Min, Max, FloatField
from django.db.models.functions import Cast

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

        elif question.type in ["select",'checkbox']:

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