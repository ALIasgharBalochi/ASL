from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Avg, Min, Max, FloatField
from django.db.models.functions import Cast
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.forms.models import Form , Process
from apps.reports.services import get_form_report


class UserReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        form = get_object_or_404(Form, pk=pk)

        report = get_form_report(form)

        return Response(report)

        

class ProcessReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        process = get_object_or_404(
            Process,
            id=pk
        )

        total_submissions = 0
        forms_report = []

        for form in process.forms.all():
            total_submissions += form.submissions.count()

            forms_report.append({
                "id": form.id,
                "report": get_form_report(form),
            })

        return Response({
            "process": process.id,
            "views": process.views,
            "total_submissions": total_submissions,
            "forms": forms_report,
        })