from rest_framework import serializers
from ....forms.models import Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "form",
            "is_requierd",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]
        
class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "text",
            "form",
            "is_requierd",
        ]
        
class QuestionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "text",
            "is_requierd",
        ]
        
class QuestionDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
        ]
        read_only_fields = [
            "id",
        ]
        
# class QuestionOptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Question
#         fields = [
#             "id",
#             "text",
#             "form",
#             "is_requierd",
#             "created_at",
#         ]
#         read_only_fields = [
#             "id",
#             "created_at",
#         ]