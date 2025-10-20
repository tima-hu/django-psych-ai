from django.urls import path
from . import views

urlpatterns = [
    path('assessments/', views.AssessmentList.as_view(), name='assessment-list'),
    path('assessments/<int:pk>/', views.AssessmentDetail.as_view(), name='assessment-detail'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('planner/', views.PlannerView.as_view(), name='planner'),
]