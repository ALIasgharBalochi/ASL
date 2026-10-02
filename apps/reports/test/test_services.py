from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.reports.services import (
    get_report_period_times,
    get_period_reporting,
)
from apps.forms.models import Form


class ReportServiceTest(TestCase):

    def test_get_report_period_times_weekly(self):
        start, end = get_report_period_times("weekly")

        self.assertEqual(end - start, timedelta(weeks=1))

    def test_get_report_period_times_monthly(self):
        start, end = get_report_period_times("monthly")

        self.assertTrue(start < end)

    def test_get_report_period_times_invalid_period(self):
        with self.assertRaises(ValueError):
            get_report_period_times("yearly")

    def test_get_period_reporting_empty(self):
        now = timezone.now()

        report = get_period_reporting(
            now - timedelta(days=7),
            now,
        )

        self.assertEqual(report["form_count"], 0)
        self.assertEqual(report["total_view"], 0)
        self.assertEqual(report["total_submissions"], 0)