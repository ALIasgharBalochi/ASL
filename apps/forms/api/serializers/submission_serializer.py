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

        question = attrs["question"]
        options = attrs.get("options")
        value = attrs.get("value")

        # this part is for checking if the text type of question has the right input(values not options)
        # it checks if there is a value and also checks that there shouldn't be an option for text type of question

        if question.type == "text":

            if not value:
                raise serializers.ValidationError({"value": "this field is required"})

            if options:
                raise serializers.ValidationError(
                    {"options": "options is not allowed for this question"}
                )

        # this part is for checking if the number type of question has the right input(values not options)
        # it checks if there is a value and also checks that there shouldn't be an option for number type of question

        if question.type == "number":

            if not value:
                raise serializers.ValidationError({"value": "this field is required"})

            if options:
                raise serializers.ValidationError(
                    {"options": "options is not allowed for this question"}
                )

            try:
                float(value)
            except (ValueError,TypeError):
                raise serializers.ValidationError({'value': 'value should be type number'})
            

        # this part is for checking if the select type of question has the right input(values not options)
        # it checks if there is at least an option and also checks that there shouldn't be an value for select type of question

        elif question.type == "select":

            if not options:
                raise serializers.ValidationError({"options": "this field is required"})

            if len(options) != 1:
                raise serializers.ValidationError(
                    {"options": "you only have to select one option"}
                )

            if value:
                raise serializers.ValidationError(
                    {"value": "value is not allowed for this question type (select)"}
                )

        # this part is for checking if the select type of question has the right input(values not options)
        # it checks if there is an option and also checks that there shouldn't be an value for checkbox type of question

        elif question.type == "checkbox":

            if not options:
                raise serializers.ValidationError({"options": "this field is required"})

            if value:
                raise serializers.ValidationError(
                    {"value": "value is not allowed for this question type (checkbox)"}
                )

        return attrs
