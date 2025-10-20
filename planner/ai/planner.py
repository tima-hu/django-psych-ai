import json
import uuid
from datetime import timedelta, date
from typing import Any, Dict, List, Tuple, Union

"""
Простой rule-based генератор learning plan.
Принимает user_data в виде dict/list/str (JSON) и возвращает структуру плана (dict).
Цель — предоставить детерминированный, безопасный пример; замените на ML/LLM-логику по необходимости.
"""

def _safe_parse(data: Union[str, dict, list, None]) -> Union[dict, list, None]:
    if data is None:
        return None
    if isinstance(data, (dict, list)):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except Exception:
            # оставляем как строку, обернём ниже
            return data
    return None

def _analyze_assessment(assessment: Any) -> Dict[str, float]:
    """
    Ожидает структуру assessment, например:
    - {'scales': {'conscientiousness': 3.2, 'neuroticism': 4.1, ...}}
    - или список вопросов с numeric answers: [{'skill':'time_management','answer':2}, ...]
    Возвращает словарь шкал/навыков с "score" (чем меньше — слабее).
    """
    scores: Dict[str, float] = {}
    if not assessment:
        return scores

    # Вариант: scales
    if isinstance(assessment, dict):
        scales = assessment.get('scales') or assessment.get('results') or assessment.get('scores')
        if isinstance(scales, dict):
            for k, v in scales.items():
                try:
                    scores[str(k)] = float(v)
                except Exception:
                    continue
            return scores

        # Вариант: items list
        items = assessment.get('items') or assessment.get('answers') or assessment.get('data')
        if isinstance(items, list):
            # агрегируем по skill/key
            agg: Dict[str, List[float]] = {}
            for it in items:
                if isinstance(it, dict):
                    key = it.get('skill') or it.get('question') or it.get('key')
                    val = it.get('answer') or it.get('score')
                    if key and isinstance(val, (int, float)):
                        agg.setdefault(key, []).append(float(val))
            for k, vals in agg.items():
                # нормируем в 0..5 (если исходно 1..5) - оставляем mean
                scores[k] = sum(vals) / len(vals) if vals else 0.0
            if scores:
                return scores

    # Если assessment — list простых чисел: вернём индексные слабости
    if isinstance(assessment, list) and assessment and all(isinstance(x, (int, float)) for x in assessment):
        for idx, v in enumerate(assessment):
            scores[f'item_{idx}'] = float(v)
        return scores

    # Ничего не разобрали
    return scores

def _rank_weaknesses(scores: Dict[str, float], top_n: int = 3) -> List[Tuple[str, float]]:
    """
    Ранжирование по возрастанию score (меньше = слабее).
    Возвращает список (key, score).
    """
    if not scores:
        return []
    # Если шкалы в разных диапазонах — нормализуем к 0..1 по min/max
    vals = list(scores.values())
    try:
        vmin, vmax = min(vals), max(vals)
        if vmax > vmin:
            norm = {k: (v - vmin) / (vmax - vmin) for k, v in scores.items()}
            # слабее -> ближе к 0, используем norm value
            ranked = sorted(norm.items(), key=lambda x: x[1])
            # возвращаем оригинальные значения для контекста
            return [(k, scores[k]) for k, _ in ranked[:top_n]]
    except Exception:
        pass
    # fallback: просто сортируем по raw value
    ranked = sorted(scores.items(), key=lambda x: x[1])
    return ranked[:top_n]

def _create_tasks_for_weakness(weak: Tuple[str, float], start_date: date, idx: int) -> Dict[str, Any]:
    key, score = weak
    # простая mapping шаблонов
    templates = {
        'time_management': ("Управление временем", "Еженедельные практики планирования и техника Pomodoro."),
        'conscientiousness': ("Дисциплина и регулярность", "Малые ежедневные привычки и трекер прогресса."),
        'neuroticism': ("Стресс-менеджмент", "Дыхательные техники, медиативные практики, работа с перфекционизмом."),
        'motivation': ("Мотивация", "Определение целей по методу SMART, маленькие выигрыши."),
        'communication': ("Коммуникация", "Ролевые упражнения, активное слушание и обратная связь."),
    }
    title, desc = templates.get(key, (f"Улучшение навыка: {key}", "Практические упражнения, ресурсы и контроль прогресса."))

    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "skill_key": key,
        "description": desc,
        "baseline_score": score,
        "priority": max(1, 5 - int(round(score))) if isinstance(score, (int, float)) else 3,
        "start_date": (start_date + timedelta(days=idx*7)).isoformat(),
        "duration_days": 14,
        "weekly_effort_hours": 2,
        "resources": [
            {"type": "article", "title": "Вводный материал", "url": "https://example.com/readme"},
            {"type": "exercise", "title": "Практическое задание", "notes": "Делать 3 раза в неделю"}
        ],
        "metrics": {
            "measure": "self_report",
            "frequency_days": 7
        }
    }
    return task

def generate_learning_plan(user_data: Union[str, dict, list, None], max_focus: int = 3) -> Dict[str, Any]:
    """
    Основная функция. Возвращает dict с планом:
    {
      "plan_id": str,
      "created_at": "YYYY-MM-DD",
      "summary": "...",
      "focus": [{"key":..., "score":...}, ...],
      "tasks": [ {...}, ... ],
      "notes": "..."
    }
    """
    parsed = _safe_parse(user_data)
    today = date.today()

    # Попытка извлечь профиль и assessment
    profile = None
    assessment = None
    if isinstance(parsed, dict):
        profile = parsed.get('profile') or parsed.get('user_profile') or parsed.get('profile_data')
        assessment = parsed.get('assessment') or parsed.get('results') or parsed.get('scales') or parsed.get('answers')
    else:
        # если передали просто assessment как list/str
        assessment = parsed

    scores = _analyze_assessment(assessment) if assessment else {}
    weaknesses = _rank_weaknesses(scores, top_n=max_focus) if scores else []

    tasks: List[Dict[str, Any]] = []
    if weaknesses:
        for idx, weak in enumerate(weaknesses):
            tasks.append(_create_tasks_for_weakness(weak, today, idx))
        summary = f"Фокус на {', '.join([w[0] for w in weaknesses])} (определено по результатам оценки)."
    else:
        # Общий план для профиля или дефолтный вводный план
        tasks = []
        # если есть профиль с предпочтениями — можно кастомизировать
        if profile and isinstance(profile, dict):
            pref = profile.get('learning_style', 'balanced')
            # простая ветвь по стилю обучения
            if pref == 'visual':
                tasks.append({
                    "id": str(uuid.uuid4()),
                    "title": "Визуальные материалы и конспекты",
                    "description": "Смотреть видео и делать схемы. 3 часа в неделю.",
                    "start_date": today.isoformat(),
                    "duration_days": 21,
                    "weekly_effort_hours": 3,
                    "resources": [{"type":"video_playlist","url":"https://example.com/videos"}]
                })
            elif pref == 'kinesthetic':
                tasks.append({
                    "id": str(uuid.uuid4()),
                    "title": "Практические проекты",
                    "description": "Проектные задания с итеративной обратной связью.",
                    "start_date": today.isoformat(),
                    "duration_days": 28,
                    "weekly_effort_hours": 4,
                    "resources": [{"type":"project","notes":"Придумать и реализовать небольшой проект"}]
                })
            else:
                tasks.append({
                    "id": str(uuid.uuid4()),
                    "title": "Базовый план развития",
                    "description": "Смешанная программа: чтение, практика, рефлексия.",
                    "start_date": today.isoformat(),
                    "duration_days": 21,
                    "weekly_effort_hours": 3,
                    "resources": [{"type":"mixed","notes":"Чередовать чтение и упражнения"}]
                })
            summary = "Персонализированный стартовый план на основе профиля."
        else:
            # дефолтный входной план
            tasks.append({
                "id": str(uuid.uuid4()),
                "title": "Оценка и планирование",
                "description": "Короткая диагностика и постановка целей (1 неделя).",
                "start_date": today.isoformat(),
                "duration_days": 7,
                "weekly_effort_hours": 1,
                "resources": [{"type":"survey","notes":"Завершить дополнительные тесты"}]
            })
            tasks.append({
                "id": str(uuid.uuid4()),
                "title": "Базовый учебный цикл",
                "description": "4-недельный цикл с заданиями и рефлексией.",
                "start_date": (today + timedelta(days=7)).isoformat(),
                "duration_days": 28,
                "weekly_effort_hours": 3,
                "resources": [{"type":"course","url":"https://example.com/course"}]
            })
            summary = "Дефолтный стартовый план."

    plan = {
        "plan_id": str(uuid.uuid4()),
        "created_at": today.isoformat(),
        "summary": summary,
        "focus": [{"key": k, "score": s} for k, s in weaknesses],
        "tasks": tasks,
        "notes": "Этот план сгенерирован rule-based функцией. Для production замените на ML/LLM pipeline."
    }
    return plan




# from sklearn.linear_model import LinearRegression
# import numpy as np

# class LearningPlanGenerator:
#     def __init__(self, user_data, course_data):
#         self.user_data = user_data
#         self.course_data = course_data

#     def analyze_user_data(self):
#         # Analyze user data to determine learning preferences and strengths
#         # This is a placeholder for actual analysis logic
#         return {
#             'learning_style': 'visual',
#             'strengths': ['math', 'science'],
#             'weaknesses': ['literature']
#         }

#     def generate_plan(self):
#         user_analysis = self.analyze_user_data()
#         # Generate a personalized learning plan based on user analysis
#         plan = {
#             'recommended_courses': self.recommend_courses(user_analysis),
#             'study_schedule': self.create_study_schedule(user_analysis)
#         }
#         return plan

#     def recommend_courses(self, user_analysis):
#         # Recommend courses based on user strengths and weaknesses
#         recommended = []
#         for course in self.course_data:
#             if course['subject'] in user_analysis['strengths']:
#                 recommended.append(course['name'])
#         return recommended

#     def create_study_schedule(self, user_analysis):
#         # Create a study schedule based on user preferences
#         schedule = {}
#         for course in self.recommend_courses(user_analysis):
#             schedule[course] = '2 hours per week'
#         return schedule

# # Example usage
# if __name__ == "__main__":
#     user_data = {'id': 1, 'name': 'John Doe'}
#     course_data = [
#         {'name': 'Math 101', 'subject': 'math'},
#         {'name': 'Science 101', 'subject': 'science'},
#         {'name': 'Literature 101', 'subject': 'literature'}
#     ]
    
#     generator = LearningPlanGenerator(user_data, course_data)
#     learning_plan = generator.generate_plan()
#     print(learning_plan)

