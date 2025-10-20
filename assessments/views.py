from django.shortcuts import render
from rest_framework import viewsets,generics
from .models import Assessment, UserResponse
from .serializers import AssessmentSerializer, UserResponseSerializer

class AssessmentList(generics.ListCreateAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
class AssessmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

class UserResponseViewSet(viewsets.ModelViewSet):
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer

def assessment_detail(request, pk):
    assessment = Assessment.objects.get(pk=pk)
    return render(request, 'assessments/detail.html', {'assessment': assessment})