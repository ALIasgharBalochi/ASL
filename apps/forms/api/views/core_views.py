from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.forms.models import Category, Process
from ..serializers.core_serializer import CategorySerializer, ProcessSerializer,ProcessPasswordSerializer
from rest_framework.response import Response
from django.db.models import F
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    # here each user gets its own categories
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        process = self.get_object()

        process.views = F("views") + 1
        process.save(update_fields=["views"])

        process.refresh_from_db()

        serializer = self.get_serializer(process)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        process = self.get_object()

        if process.password:
            return Response({
                "detail": "this process is password protected"
            })

        return Response(ProcessSerializer(process).data)

    # for unlocking a process you should post a password
    @action(detail=True, methods=["post"], url_path="unlock")
    def unlock(self, request, pk=None):
        process = self.get_object()

        serializer = ProcessPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data["password"]

        if process.password and not process.check_password(password):
            raise PermissionDenied("password is incorrect")

        return Response(ProcessSerializer(process).data)

    