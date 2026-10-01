from apps.accounts.api.serializers.reset_password_serializers import (
    RequestResetPasswordSerializer,
)
from apps.accounts.services import AccountService
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


class ResetPasswordAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RequestResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        finder_id, otp = AccountService.generat_register_otp()

        if user and finder_id and otp:

            finder = AccountService.set_data_registratoin_to_redis(
                data=serializer.validated_data,
                key=f"finder_id:{finder_id}",
                duratoin=300,
            )

            if not finder:
                return Response(
                    {"message": "your process failed please try later"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            otp_saved = AccountService.set_data_registratoin_to_redis(
                data={"otp": otp}, key=f"finder_id:{finder_id}:otp", duratoin=120
            )

            if not otp_saved:
                return Response(
                    {"message": "your otp creation got failed, try again later"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            code = AccountService.send_email_registratoin(
                otp=otp, email=email, subject="otp for changing password"
            )

            if code == 1:
                return Response(
                    {
                        "message": "we send you an email contain the otp change password code, please check your inbox.",
                        "finder_id": finder_id,
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                AccountService.delete_registration_data(
                    f"finder_id:{finder_id}",
                    f"finder_id:{finder_id}:otp"
                )

                return Response(
                    {
                        "message": "failed to send the otp.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
