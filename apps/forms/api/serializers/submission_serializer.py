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

        question = attrs['question']
        options = attrs.get("options")
        value = attrs.get("value")

        # this part is for checking if the number and text type of question has the right input(values not options)

        if question.type in ['number','text']:

            if not value:
                raise serializers.ValidationError(
                    {'value':'this field is required'}
                )

            if options:
                raise serializers.ValidationError(
                    {'options':'options is not allowed for this question'}
                )


        return attrs
