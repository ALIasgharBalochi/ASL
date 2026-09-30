from django.urls import path

from .views.user_statistic_views import (
    UserReportAPIView,
    ProcessReportAPIView,
    PeriodReportingView,
)

urlpatterns = [
    path(
        "<uuid:pk>/reports",
        UserReportAPIView.as_view(),
        name="user-form-report",
    ),
    path(
        "processes/<int:pk>/report/",
        ProcessReportAPIView.as_view(),
        name="process-report",
    ),
    path(
        "period/report/",
        PeriodReportingView.as_view(),
        name="period_report",
    ),
]