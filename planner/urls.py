from django.urls import path
from . import views

urlpatterns = [
    # Основной API: GET - список планов (параметр ?limit=), POST - создать новый план (JSON)
    path('', views.PlannerView.as_view(), name='planner'),

    # Функциональные endpoint'ы (function-based views), пригодны для form POST / просмотра в браузере
    path('create/', views.create_learning_plan, name='create-learning-plan'),      # POST form -> создаёт план и возвращает JSON
    path('plans/<int:plan_id>/', views.view_learning_plan, name='view-learning-plan'),  # рендерит HTML-шаблон с планом
]