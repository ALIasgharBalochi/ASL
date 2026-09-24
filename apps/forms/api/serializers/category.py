from rest_framework import serializers
from ....forms.models import Category, Form

class CategorySerializer(serializers.ModelSerializer):

    forms = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    process = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["name", "created_at", "forms", "process"]
        read_only_fields = ["created_at"]