from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Avg, Min, Max, FloatField
from django.db.models.functions import Cast
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.forms.models import Form


class UserReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        form = get_object_or_404(Form, pk=pk)

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


        return Response(report)
