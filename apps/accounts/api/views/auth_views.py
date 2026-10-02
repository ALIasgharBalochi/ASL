from ..serializers.auth_serializers import (
    ReGenerateOtp,
    RegistrationSerializer,
    VerifyOtpSerialiser,
)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from ...services import AccountService
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistratoinView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serialiser = RegistrationSerializer(data=request.data)

        serialiser.is_valid(raise_exception=True)
        registratin_id, otp_code = AccountService.generat_register_otp()

        if registratin_id and otp_code:

            is_saved_data = AccountService.set_data_registratoin_to_redis(
                serialiser.validated_data, f"registration:{registratin_id}", 600
            )

            if not is_saved_data:
                return Response({"message": "registration failed"}, status=400)

            is_saved_otp = AccountService.set_data_registratoin_to_redis(
                {"otp": otp_code}, f"registration:{registratin_id}:otp", 120
            )

            if not is_saved_otp:
                return Response({"message": "faile save otp"}, status=400)

            sending_code = AccountService.send_email_registratoin(
                f"your otp code is : {otp_code}",
                serialiser.validated_data["email"],
                "OTP code",
            )

            print(otp_code)
            return Response(
                {
                    "message": "code send successfuly",
                    "regestratoin_id": registratin_id,
                },
                status=200,
            )
            # if sending_code == 1:
            #     return Response(
            #         {
            #             "message": "code send successfuly",
            #             "regestratoin_id": registratin_id,
            #         },
            #         status=200,
            #     )
            # else:
            #     AccountService.delete_registration_data(
            #         f"registration:{registratin_id}",
            #         f"registration:{registratin_id}:otp",
            #     )
            #     return Response({"message": "send otp faield"}, status=400)


class VerifyOtp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOtpSerialiser(data=request.data)

        serializer.is_valid(raise_exception=True)
        registration_id = serializer.validated_data["registration_id"]
        can_verify = AccountService.can_verify_otp(registration_id)

        if can_verify:

            is_verified = AccountService.verify_otp(
                serializer.validated_data["otp"],
                f"registration:{registration_id}:otp",
            )

            if is_verified:
                data = AccountService.get_data_in_redis(
                    f"registration:{registration_id}"
                )
                if data:
                    data = {k.decode(): v.decode() for k, v in data.items()}
                    User.objects.create(**data)
                    AccountService.delete_registration_data(
                        f"registration:{registration_id}",
                        f"registration:{registration_id}:otp",
                    )
                    AccountService.delete_registration_data(
                        f"otp:verify:attempts:{registration_id}"
                    )
                    return Response(
                        {"message": "user create success fully"}, status=200
                    )
                return Response({"message": "verify failed"}, status=400)
                # return Response({"message": "user create successfully"}, status=200)
            return Response({"message": "verify failed"}, status=400)
        else:
            return Response(
                {"message": "Too many attempts. Please try again in 5 minutes."},
                status=429,
            )


class RegenerateOtp(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ReGenerateOtp(data=request.data)

        serializer.is_valid(raise_exception=True)

        registratoin_id = serializer.validated_data["registration_id"]

        old_otp_code = AccountService.get_data_in_redis(
            f"registration:{registratoin_id}:otp"
        )
        if not old_otp_code:
            re_id, otp_code = AccountService.generat_register_otp()
            AccountService.set_data_registratoin_to_redis(
                {"otp": otp_code}, f"registration:{registratoin_id}:otp", 120
            )
            data = AccountService.get_data_in_redis(f"registration:{registratoin_id}")
            sending_code = AccountService.send_email_registratoin(
                f"your otp code is : {otp_code}",
                data[b"email"].decode(),
                "OTP code",
            )
            print(otp_code)
            return Response(
                {
                    "message": "code send successfuly",
                    "regestratoin_id": registratoin_id,
                },
                status=200,
            )
            # if sending_code == 1:

            #     return Response(
            #         {
            #             "message": "code send successfuly",
            #             "regestratoin_id": registratoin_id,
            #         },
            #         status=200,
            #     )
            # else:
            #     AccountService.delete_registration_data(
            #         f"registration:{registratoin_id}",
            #         f"registration:{registratoin_id}:otp",
            #     )
            #     return Response({"message": "send otp faield"}, status=400)
        else:
            return Response({"message": "Your old code is still valid."}, status=400)
