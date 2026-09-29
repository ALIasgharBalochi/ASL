from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from apps.forms.models import Form, Process
from apps.reports.services import (
    get_form_report,
    get_report_period_times,
    get_period_reporting,
)


@method_decorator(cache_page(60), name="dispatch")
class UserReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        form = get_object_or_404(Form, pk=pk)

        report = get_form_report(form)

        return Response(report)


@method_decorator(cache_page(60), name="dispatch")
class ProcessReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        process = get_object_or_404(Process, id=pk)

        total_submissions = 0
        forms_report = []

        for form in process.forms.all():
            total_submissions += form.submissions.count()

            forms_report.append(
                {
                    "id": form.id,
                    "report": get_form_report(form),
                }
            )

        return Response(
            {
                "process": process.id,
                "views": process.views,
                "total_submissions": total_submissions,
                "forms": forms_report,
            }
        )


class PeriodReportingView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):
        period = request.query_params.get("period")

        if period not in ["weekly", "monthly"]:
            return Response(
                {"detail": "Invalid period. Allowed values are: weekly, monthly."},
                status=400,
            )

        start, end = get_report_period_times(period)

        key = f"period-report:{period}:{start}:{end}"

        data = cache.get(key)

        if data is None:
            data = get_period_reporting(start, end)
            cache.set(key, data, timeout=60 * 5)

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
