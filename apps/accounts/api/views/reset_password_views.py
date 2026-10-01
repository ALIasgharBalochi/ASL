from apps.accounts.api.serializers.reset_password_serializers import RequestResetPasswordSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class ResetPasswordAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self,request):

        serializer = RequestResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user  = User.objects.filter(email=email).first()

