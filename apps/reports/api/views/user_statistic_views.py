from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from apps.forms.models import Form, Process
from apps.reports.services import (
    get_form_report,
    get_report_period_times,
    get_period_reporting,
)


class UserReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        form = get_object_or_404(Form, pk=pk)

        report = get_form_report(form)

        return Response(report)


class ProcessReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        process = get_object_or_404(Process, id=pk)

        total_views = 0
        total_submissions = 0
        forms_report = []

        for form in process.forms.all():
            total_views += form.views
            total_submissions += form.submissions.count()

            forms_report.append({
                "id": form.id,
                "views": form.views,
                "report": get_form_report(form),
            })

        return Response(
            {
                "process": process.id,
                "views": total_views,
                "total_submissions": total_submissions,
                "forms": forms_report,
            }
        )


class PeriodReportingView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):
        period = request.query_params.get("period")

        if not period == "weekly" and not period == "monthly":
            return Response(
                {"detail": "Invalid period. Allowed values are: weekly, monthly."},
                status=400,
            )
        start, end = get_report_period_times(period)

        data: dict = get_period_reporting(start, end)

        return Response(
            {
                "period": {
                    "type": period,
                    "start": start,
                    "end": end,
                },
                "summary": data,
            }
        )
