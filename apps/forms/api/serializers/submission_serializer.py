from rest_framework import serializers
from ...models import Submission, Answer, AnswerOption, Question, QuestionOption


class SubmissionSerializer(serializers.ModelSerializer):
    answers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

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
    selected_options = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

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


class SubmitAnswerSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    value = serializers.CharField(required=False)
    options = serializers.PrimaryKeyRelatedField(
        queryset=QuestionOption.objects.all(), many=True, required=False
    )

    def validate(self, attrs):
        if not attrs.get("options") and not attrs.get("value"):
            raise serializers.ValidationError("options or value is required ")
        return attrs
