from apps.accounts.api.serializers.reset_password_serializers import (
    RequestResetPasswordSerializer,
    VerifyResetPasswordOTPSerializer,
    ChangeResetPasswordSerializer,
)
from apps.accounts.services import AccountService
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from django_redis import get_redis_connection

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
                    f"finder_id:{finder_id}", f"finder_id:{finder_id}:otp"
                )

                return Response(
                    {
                        "message": "failed to send the otp.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )


class VerifyResetPasswordOTPAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serilizer = VerifyResetPasswordOTPSerializer(data=request.data)
        serilizer.is_valid(raise_exception=True)

        finder_id = serilizer.validated_data["finder_id"]
        otp = serilizer.validated_data["otp"]

        is_verified = AccountService.verify_otp(
            otp=otp, key=f"finder_id:{finder_id}:otp"
        )

        if not is_verified:
            return Response(
                {"message": "your verification failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        redis = get_redis_connection("default")
        verified_key = f"finder_id:{finder_id}:verified"
        redis.set(verified_key, 1, ex=300)

        return Response(
            {"message": "otp verify successfully"}, status=status.HTTP_200_OK
        )


class ChangeResetPasswordAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serilizer = ChangeResetPasswordSerializer(data=request.data)
        serilizer.is_valid(raise_exception=True)

        finder_id = serilizer.validated_data["finder_id"]

        redis = get_redis_connection("default")

        verified_key = f"finder_id:{finder_id}:verified"

        is_verified = redis.exists(verified_key)

        if not is_verified:
            return Response(
                {"message": "your verification invalid or expired"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = AccountService.get_data_in_redis(f"finder_id:{finder_id}")

        email = data[b"email"].decode()

        user = User.objects.filter(email=email).first()

        new_password = serilizer.validated_data["new_password"]

        if not user:
            return Response(
                {"message": "user with this email not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.set_password(new_password)

        user.save()

        AccountService.delete_registration_data(verified_key, f"finder_id:{finder_id}")

        return Response(
            {"message": "your password changed successfully"}, status=status.HTTP_200_OK
        )
