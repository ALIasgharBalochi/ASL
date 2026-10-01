from rest_framework import serializers

class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyResetPasswordOTPSerializer(serializers.Serializer):
    finder_id = serializers.UUIDField()
    otp = serializers.CharField()