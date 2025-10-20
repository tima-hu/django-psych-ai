# ...existing code...
from django.shortcuts import render
from django.http import JsonResponse
from .models import LearningPlan
from .ai.planner import generate_learning_plan
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def create_learning_plan(request):
    if request.method == 'POST':
        user_data = request.POST.get('user_data')
        learning_plan = generate_learning_plan(user_data)
        new_plan = LearningPlan.objects.create(user_data=user_data, plan=learning_plan)
        return JsonResponse({'plan_id': new_plan.id, 'plan': learning_plan}, status=201)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def view_learning_plan(request, plan_id):
    try:
        plan = LearningPlan.objects.get(id=plan_id)
        return render(request, 'planner/plan.html', {'plan': plan})
    except LearningPlan.DoesNotExist:
        return JsonResponse({'error': 'Plan not found'}, status=404)
    
# ...existing code...
class PlannerView(APIView):
    """
    Улучшенный PlannerView:
    - GET: возвращает последние планы (параметр ?limit=)
    - POST: принимает JSON { "user_data": { ... } } или { "assessment": {...} },
            генерирует план через generate_learning_plan, сохраняет LearningPlan и возвращает результат.
    Замечание: добавить аутентификацию/permissions в production.
    """
    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 10))
            limit = max(1, min(limit, 100))
        except Exception:
            limit = 10

        plans_qs = LearningPlan.objects.all().order_by('-created_at')[:limit]
        plans = []
        for p in plans_qs:
            plans.append({
                "id": p.id,
                "created_at": getattr(p, "created_at", None),
                "user_data": p.user_data if hasattr(p, "user_data") else None,
                "plan_summary": (p.plan[:200] if isinstance(p.plan, str) else p.plan)  # краткое представление
            })

        return Response({"count": len(plans), "plans": plans}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Ожидает JSON:
        {
          "user_data": {...}          
          // либо
          "assessment": {...}         # данные теста/результаты
        }
        """
        payload = request.data
        user_data = payload.get('user_data') or payload.get('assessment')
        if not user_data:
            return Response({"error": "Missing 'user_data' or 'assessment' in request body."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Простая валидация: user_data должен быть dict или сериализуемым в JSON
        if not isinstance(user_data, (dict, list, str)):
            return Response({"error": "'user_data' must be a dict, list or string."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            # Здесь ваша логика генерации — вызывает модуль ai.planner
            learning_plan = generate_learning_plan(user_data)

            # Сохранение в БД
            new_plan = LearningPlan.objects.create(user_data=user_data, plan=learning_plan)

            response_data = {
                "plan_id": new_plan.id,
                "plan": learning_plan
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Error generating learning plan")
            return Response({"error": "Failed to generate learning plan", "detail": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ...existing code...