from django.urls import path

from .consumers import FormReportConsumer

websocket_urlpatterns = [
    path(
        "ws/reporting/forms/<uuid:form_id>/",
        FormReportConsumer.as_asgi(),
    ),
]
