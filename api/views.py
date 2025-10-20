# api/views.py
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Assessment, User
from .serializers import AssessmentSerializer, UserSerializer

# --------------------------
# Assessments
# --------------------------
class AssessmentList(generics.ListCreateAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

class AssessmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

# --------------------------
# Users
# --------------------------
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# --------------------------
# Planner
# --------------------------
class PlannerView(APIView):
    """
    Пример простого PlannerView, возвращающего фиктивные данные.
    Замените на вашу бизнес-логику.
    """
    def get(self, request):
        data = {
            "message": "Planner data here",
            "tasks": [
                {"id": 1, "title": "Task 1", "done": False},
                {"id": 2, "title": "Task 2", "done": True},
            ],
        }
        return Response(data, status=status.HTTP_200_OK)
