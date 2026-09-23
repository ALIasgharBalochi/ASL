from rest_framework import serializers
from ...models import Form



class FormSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )


    class Meta:
        model = Form

        fields = [
            "id",
            "visibility",
            "proces",
            "password",
            "category",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]
        
    def create(self, validated_data):
        password = validated_data.pop("password")
        form = Form.objects.create(**validated_data)
        form.set_password(password)
        form.save()
        return form