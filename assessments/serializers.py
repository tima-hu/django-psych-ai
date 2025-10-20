from rest_framework import serializers
from .models import PsychologicalTest, UserResponse

class PsychologicalTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PsychologicalTest
        fields = '__all__'

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = '__all__'