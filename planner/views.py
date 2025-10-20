from django.shortcuts import render
from django.http import JsonResponse
from .models import LearningPlan
from .ai.planner import generate_learning_plan

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