from django.urls import path
from assessments.views import AssessmentDetail,AssessmentList
from users.views import UserList,UserDetail
from planner.views import  PlannerView

urlpatterns = [
    path('assessments/', AssessmentList.as_view(), name='assessment-list'),
    path('assessments/<int:pk>/', AssessmentDetail.as_view(), name='assessment-detail'),
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('planner/', PlannerView.as_view(), name='planner'),
]