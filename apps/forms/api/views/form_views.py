from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import status
from apps.forms.models import Form, Question, QuestionOption
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from ..serializers.form_serializer import (
    FormSerializer,
    FormPasswordSerializer,
    QuestionSerializer,
    QuestionOptionSerializer,
)
from rest_framework.reverse import reverse

from django.db.models import F


class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return Form.objects.all()

    def get_permissions(self):

        if self.action in ["retrieve", "unlock"]:
            return [AllowAny()]

        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):

        form = self.get_object()

        form.views = F("views") + 1
        form.save(update_fields=["views"])
        form.refresh_from_db()

        if form.password:
            return Response({"detail": "this form is password protected"})

        serializer = self.get_serializer(form)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"], url_path="unlock")
    def unlock(self, request, id=None):

        form = self.get_object()

        serializer = FormPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data["password"]

        if not form.password:
            return Response(FormSerializer(form).data)

        if form.check_password(password):
            return Response(FormSerializer(form).data)
        else:
            raise PermissionDenied("password is incorrect")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        form = serializer.save()

        public_link = request.build_absolute_uri(
            reverse("form-detail", kwargs={"id": form.id}, request=request)
        )

        return Response(
            {"form": serializer.data, "public_link": public_link},
            status=status.HTTP_201_CREATED,
        )


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return Question.objects.all()


class QuestionOptionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionOptionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return QuestionOption.objects.all()
