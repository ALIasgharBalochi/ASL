from rest_framework import serializers
from ....forms.models import Category

class CategorySerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Category
        
        fields = [
            
            "name",
            "created_at", 
        ]
        
        read_only_fields = [
            
                    "created_at",
                ]