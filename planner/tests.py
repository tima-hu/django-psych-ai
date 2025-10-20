from django.test import TestCase
from .models import Plan

class PlanModelTest(TestCase):

    def setUp(self):
        self.plan = Plan.objects.create(
            title="Test Plan",
            description="This is a test plan for learning.",
            duration=30
        )

    def test_plan_creation(self):
        self.assertEqual(self.plan.title, "Test Plan")
        self.assertEqual(self.plan.description, "This is a test plan for learning.")
        self.assertEqual(self.plan.duration, 30)

    def test_plan_str(self):
        self.assertEqual(str(self.plan), "Test Plan")