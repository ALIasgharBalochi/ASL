from rest_framework import serializers

class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()