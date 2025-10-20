from rest_framework import serializers
from .models import PsychologicalTest, UserResponse,Assessment
from users.serializers import UserSerializer
from users.models import CustomUser
class PsychologicalTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PsychologicalTest
        fields = '__all__'

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), source='user', write_only=True, required=False)

    class Meta:
        model = Assessment
        fields = ['id', 'title', 'description', 'data', 'results', 'score', 'user', 'user_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'results', 'score']

    def validate_data(self, value):
        # Простая валидация: ожидаем список вопросов или словарь
        if not isinstance(value, (list, dict)):
            raise serializers.ValidationError("Поле data должно быть списком или словарём с вопросами.")
        return value