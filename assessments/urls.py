from django.urls import path
from . import views

urlpatterns = [
    path('tests/', views.TestListView.as_view(), name='test_list'),
    path('tests/<int:pk>/', views.TestDetailView.as_view(), name='test_detail'),
    path('tests/<int:pk>/results/', views.TestResultsView.as_view(), name='test_results'),
]