from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class VerifyOtpSerialiser(serializers.Serializer):
    registration_id = serializers.UUIDField()
    otp = serializers.CharField()

    def validate_otp(self, value: str):

        if not value.isnumeric():
            raise serializers.ValidationError("otp shold be number")

        return value


class ReGenerateOtp(serializers.Serializer):
    registration_id = serializers.UUIDField()
