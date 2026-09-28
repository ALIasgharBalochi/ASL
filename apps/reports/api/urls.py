from django.urls import path
from .views.user_statistic_views import UserReportAPIView

urlpatterns = [
    path('<uuid:pk>/reports',UserReportAPIView.as_view(),name='user-form-report')
]