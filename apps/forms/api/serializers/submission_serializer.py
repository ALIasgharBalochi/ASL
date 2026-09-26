from rest_framework import serializers
from forms.models import Submission, Answer, AnswerOption


class SubmissionSerializer(serializers.ModelSerializer):
    answers = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Submission
        fields = [
            "id",
            "form",
            "user",
            "created_at",
            "answers",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "answers",
        ]


class AnswerSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Answer
        fields = [
            "id",
            "submission",
            "question",
            "value",
            "created_at",
            "selected_options",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "selected_options",
        ]


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = [
            "id",
            "answer",
            "option",
        ]
        read_only_fields = [
            "id",
        ]