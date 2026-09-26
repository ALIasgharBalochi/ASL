from rest_framework import serializers
from apps.forms.models import Form, Question, QuestionOption


class FormSerializer(serializers.ModelSerializer):
    questions = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

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
        model = Form
        fields = [
            "id",
            "visibility",
            "procces",
            "password",
            "category",
            "created_at",
            "questions",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "questions",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", None)

        form = Form.objects.create(**validated_data)
        form.set_password(password)
        form.save()

        return form

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance


class FormPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="پسورد فرم را وارد کنید"
    )


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = [
            "id",
            "question",
            "value",
        ]
        read_only_fields = [
            "id",
        ]

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True)
    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "form",
            "is_required",
            "options",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def create(self, validated_data):

        options_data = validated_data.pop("options")

        question = Question.objects.create(**validated_data)

        for option_data in options_data:
            QuestionOption.objects.create(
                question=question,
                **option_data
            )

        return question