from rest_framework import serializers
from apps.forms.models import Category, Process


class CategorySerializer(serializers.ModelSerializer):
    
    forms = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    process = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "created_at",
            "forms",
            "process",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "forms",
            "processes",
        ]


class ProcessSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Leave empty if no change is needed",
        style={
            "input_type": "password",
            "placeholder": "Password",
        },
    )

    class Meta:
        model = Process
        fields = [
            "id",
            "user",
            "visibility",
            "type",
            "category",
            "password",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        process = Process.objects.create(**validated_data)
        process.set_password(password)
        process.save()

        return process

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance