from django.test import TestCase
from django.contrib.auth import get_user_model
from questions.models import Question, Category
from practice.models import Interaction
from .models import ScoringHistory

User = get_user_model()


class ScoringModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Python')
        self.question = Question.objects.create(
            title='什么是Python？',
            answer='Python是一种编程语言。',
            category=self.category,
            difficulty=1
        )
        self.interaction = Interaction.objects.create(
            user=self.user,
            question=self.question,
            answer='Python是一门编程语言。',
            is_submitted=True
        )

    def test_scoring_history_creation(self):
        scoring_history = ScoringHistory.objects.create(
            interaction=self.interaction,
            scoring_method='embedding',
            score=85.5
        )
        self.assertEqual(scoring_history.interaction, self.interaction)
        self.assertEqual(scoring_history.scoring_method, 'embedding')
        self.assertEqual(scoring_history.score, 85.5)

    def test_scoring_history_str(self):
        scoring_history = ScoringHistory.objects.create(
            interaction=self.interaction,
            scoring_method='embedding',
            score=85.5
        )
        expected_str = f"{self.user.username} - embedding: 85.5"
        self.assertEqual(str(scoring_history), expected_str)
