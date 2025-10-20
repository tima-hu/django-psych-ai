from celery import shared_task
from .ai.planner import generate_learning_plan

@shared_task
def create_learning_plan(user_id, assessment_results):
    """
    Задача для создания персонализированного плана обучения на основе результатов тестирования.
    """
    plan = generate_learning_plan(user_id, assessment_results)
    # Здесь можно добавить логику для сохранения плана в базе данных или отправки пользователю
    return plan