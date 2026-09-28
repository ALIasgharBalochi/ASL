from django.shortcuts import get_object_or_404
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

                for answer in answers:

                    values.append(float(answer.value))

                if values:
                    statistic = {
                        "sum": sum(values),
                        "count": len(values),
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                    }

                else:
                    statistic = {
                        "sum": 0,
                        "count": 0,
                        "average": None,
                        "min": None,
                        "max": None,
                    }

                report.append(
                    {
                        "question": question.text,
                        "type": question.type,
                        "statistic": statistic,
                    }
                )

            elif question.type == "select":
                pass

            elif question.type == "checkbox":
                pass

        return Response(report)
