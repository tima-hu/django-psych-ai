from django.test import TestCase
from .models import Assessment, UserResponse

class AssessmentModelTest(TestCase):
    def setUp(self):
        self.assessment = Assessment.objects.create(
            title="Sample Assessment",
            description="This is a sample assessment for testing."
        )

    def test_assessment_creation(self):
        self.assertEqual(self.assessment.title, "Sample Assessment")
        self.assertEqual(self.assessment.description, "This is a sample assessment for testing.")

class UserResponseModelTest(TestCase):
    def setUp(self):
        self.assessment = Assessment.objects.create(
            title="Sample Assessment",
            description="This is a sample assessment for testing."
        )
        self.user_response = UserResponse.objects.create(
            assessment=self.assessment,
            user_id=1,
            response_data={"question_1": "answer_1"}
        )

    def test_user_response_creation(self):
        self.assertEqual(self.user_response.assessment, self.assessment)
        self.assertEqual(self.user_response.user_id, 1)
        self.assertEqual(self.user_response.response_data, {"question_1": "answer_1"})