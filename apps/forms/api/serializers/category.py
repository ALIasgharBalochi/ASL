from rest_framework import serializers
from ....forms.models import Category, Form

class CategorySerializer(serializers.ModelSerializer):
    
    form = serializers.RelatedField(many=True)
    process = serializers.RelatedField(many=True)
    
    
    
    
    class Meta:
        model = Category
        
        fields = [
            
            "name",
            "created_at", 
        ]
        
        read_only_fields = [
            
                    "created_at",
                ]