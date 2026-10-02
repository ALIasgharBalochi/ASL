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
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

User = get_user_model()


class ResetPasswordAPIView(APIView):
    """Request a password reset by creating a temporary reset token and OTP."""

    permission_classes = [AllowAny]

    @extend_schema(request=RequestResetPasswordSerializer)
    def post(self, request):
        """Send a reset OTP to the user's email if the account exists."""
        # Validate the request body before doing any reset-related work.
        serializer = RequestResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = get_object_or_404(User, email=email)

        # Generate a temporary reset identifier and a one-time password.
        finder_id, otp = AccountService.generat_register_otp()

        if user and finder_id and otp:
            # Store the reset email payload in Redis so the later steps can validate it.
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

            # Save the OTP separately for verification and limit the lifetime.
            otp_saved = AccountService.set_data_registratoin_to_redis(
                data={"otp": otp}, key=f"finder_id:{finder_id}:otp", duratoin=120
            )

            if not otp_saved:
                return Response(
                    {"message": "your otp creation got failed, try again later"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Send the OTP message to the user and clean up on failure.
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
    """Verify that the provided OTP matches the stored reset code."""

    permission_classes = [AllowAny]

    @extend_schema(request=VerifyResetPasswordOTPSerializer)
    def post(self, request):
        """Accept the OTP and mark the reset flow as verified for a short time."""
        # Validate the OTP input and the reset identifier.
        serilizer = VerifyResetPasswordOTPSerializer(data=request.data)
        serilizer.is_valid(raise_exception=True)

        finder_id = serilizer.validated_data["finder_id"]
        otp = serilizer.validated_data["otp"]

        can_verify = AccountService.can_verify_otp(finder_id)

        if can_verify:

            is_verified = AccountService.verify_otp(
                otp=otp, key=f"finder_id:{finder_id}:otp"
            )

            if not is_verified:
                return Response(
                    {"message": "your verification failed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Store a verification flag so the final password-change step can confirm the flow.
            redis = get_redis_connection("default")
            verified_key = f"finder_id:{finder_id}:verified"
            redis.set(verified_key, 1, ex=300)

            AccountService.delete_registration_data(f"otp:verify:attempts:{finder_id}")
            return Response(
                {"message": "otp verify successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Too many attempts. Please try again in 5 minutes."},
                status=429,
            )


class ChangeResetPasswordAPIView(APIView):
    """Update the user's password only after the OTP has been successfully verified."""

    permission_classes = [AllowAny]

    @extend_schema(request=ChangeResetPasswordSerializer)
    def post(self, request):
        """Change the user's password once the reset OTP verification is valid."""
        # Validate the final reset payload before mutating the user password.
        serilizer = ChangeResetPasswordSerializer(data=request.data)
        serilizer.is_valid(raise_exception=True)

        finder_id = serilizer.validated_data["finder_id"]

        redis = get_redis_connection("default")

        verified_key = f"finder_id:{finder_id}:verified"

        # Only allow password changes when the OTP verification key exists and is valid.
        is_verified = redis.exists(verified_key)

        if not is_verified:
            return Response(
                {"message": "your verification invalid or expired"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = AccountService.get_data_in_redis(f"finder_id:{finder_id}")

        email = data[b"email"].decode()

        user = get_object_or_404(User, email=email)

        new_password = serilizer.validated_data["new_password"]

        if not user:
            return Response(
                {"message": "user with this email not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Hash the new password and persist it to the user record.
        user.set_password(new_password)
        user.save()

        # Remove the temporary reset state after a successful password change.
        AccountService.delete_registration_data(verified_key, f"finder_id:{finder_id}")

        return Response(
            {"message": "your password changed successfully"}, status=status.HTTP_200_OK
        )
