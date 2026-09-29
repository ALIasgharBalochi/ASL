from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# from rest_framework import status
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

    @method_decorator(cache_page(60 * 5))
    def retrieve(self, request, *args, **kwargs):

        form = self.get_object()

        if form.password:
            return Response({"detail": "this form is password pritected"})

        serializer = self.get_serializer(form)

        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="unlock")
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


@method_decorator(cache_page(60 * 5), name="list")
@method_decorator(cache_page(60 * 5), name="retrieve")
class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return Question.objects.all()


@method_decorator(cache_page(60 * 5), name="list")
@method_decorator(cache_page(60 * 5), name="retrieve")
class QuestionOptionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionOptionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return QuestionOption.objects.all()
