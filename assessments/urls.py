from django.urls import path
from . import views

def _as_view(name):
    v = getattr(views, name, None)
    return v.as_view() if v and hasattr(v, 'as_view') else v

urlpatterns = [
    path('', _as_view('AssessmentList'), name='assessment-list'),
    path('<int:pk>/', _as_view('AssessmentDetail'), name='assessment-detail'),

    # маршруты для запуска/отправки теста и получения результатов.
    # Поддерживает как function-based (take_assessment) так и class-based (TakeAssessment) views.
    # path('<int:pk>/take/', _as_view('TakeAssessment') or _as_view('take_assessment'), name='assessment-take'),
    # path('<int:pk>/submit/', _as_view('SubmitAssessment') or _as_view('submit_assessment'), name='assessment-submit'),
    # path('<int:pk>/results/', _as_view('AssessmentResults') or _as_view('assessment_results'), name='assessment-results'),
]