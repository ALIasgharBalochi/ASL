from rest_framework import serializers

class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyResetPasswordOTPSerializer(serializers.Serializer):
    finder_id = serializers.UUIDField()
    otp = serializers.CharField()

class ChangeResetPasswordSerializer(serializers.Serializer):
    finder_id = serializers.UUIDField()
    new_password = serializers.CharField()
    verify_password = serializers.CharField()

    def validate(self, attrs):
        new_password = attrs['new_password']
        verify_password = attrs['verify_password']

        if new_password != verify_password:
            return serializers.ValidationError(
                'password do not match'
            )

        return attrs