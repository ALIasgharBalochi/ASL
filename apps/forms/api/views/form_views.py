from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework import status
from apps.forms.models import Form, Question, QuestionOption
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from ..serializers.form_serializer import FormSerializer, FormPasswordSerializer


class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"        
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return Form.objects.filter(procces__user=self.request.user)

    
    @action(detail=True, methods=["post"], url_path="unlock")
    def unlock(self, request, pk=None):
        """
        POST /forms/api/forms/<uuid>/unlock/
        Body: { "password": "...." }
        """
        form = self.get_object()

        serializer = FormPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data["password"]

    
        if not form.password:
            return Response(FormSerializer(form).data)

        
        if form.check_password(password):
            return Response(FormSerializer(form).data)
        else:
            raise PermissionDenied("pass is false khar")