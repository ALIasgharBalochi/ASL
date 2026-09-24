from rest_framework import serializers
from ....forms.models import Process

class ProcessSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(
            write_only=True,
            required=False,                     
            allow_blank=True,
            help_text='Leave empty if no change needed',
            style={'input_type': 'password', 'placeholder': 'Password'},
        )
    
    
    class Meta:
        
        model = Process
        
        fields = [
            
            "user",
            "visibility",
            "type",
            "category",
            "password",
            "created_at",
        
        ]
        
        read_only_fields = [

                    "created_at",
                ]
        
    def create(self, validated_data):
            password = validated_data.pop("password")
            form = Process.objects.create(**validated_data)
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