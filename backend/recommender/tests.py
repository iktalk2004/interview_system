from django.test import TestCase
from django.contrib.auth import get_user_model
from questions.models import Question, Category
from practice.models import Interaction
from recommender.models import UserSimilarity, QuestionSimilarity, Recommendation, UserPreference
from recommender.algorithms import CollaborativeFiltering

User = get_user_model()


class CollaborativeFilteringTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

        self.category = Category.objects.create(name='Python')
        self.question1 = Question.objects.create(
            title='问题1',
            answer='答案1',
            category=self.category,
            difficulty=1
        )
        self.question2 = Question.objects.create(
            title='问题2',
            answer='答案2',
            category=self.category,
            difficulty=2
        )

    def test_calculate_user_similarity(self):
        Interaction.objects.create(
            user=self.user1,
            question=self.question1,
            answer='答案1',
            score=85,
            is_submitted=True
        )
        Interaction.objects.create(
            user=self.user2,
            question=self.question1,
            answer='答案1',
            score=90,
            is_submitted=True
        )

        similarity = CollaborativeFiltering.calculate_user_similarity(
            self.user1, self.user2, min_common_questions=1
        )

        self.assertGreaterEqual(similarity, 0)
        self.assertLessEqual(similarity, 1)

    def test_calculate_question_similarity(self):
        Interaction.objects.create(
            user=self.user1,
            question=self.question1,
            answer='答案1',
            score=85,
            is_submitted=True
        )
        Interaction.objects.create(
            user=self.user1,
            question=self.question2,
            answer='答案2',
            score=75,
            is_submitted=True
        )

        similarity = CollaborativeFiltering.calculate_question_similarity(
            self.question1, self.question2, min_common_users=1
        )

        self.assertGreaterEqual(similarity, 0)
        self.assertLessEqual(similarity, 1)

    def test_user_based_recommend(self):
        Interaction.objects.create(
            user=self.user1,
            question=self.question1,
            answer='答案1',
            score=85,
            is_submitted=True
        )
        Interaction.objects.create(
            user=self.user2,
            question=self.question1,
            answer='答案1',
            score=90,
            is_submitted=True
        )
        Interaction.objects.create(
            user=self.user2,
            question=self.question2,
            answer='答案2',
            score=80,
            is_submitted=True
        )

        recommendations = CollaborativeFiltering.user_based_recommend(
            self.user1, n=5, min_similarity=0.1
        )

        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)

    def test_update_user_preferences(self):
        Interaction.objects.create(
            user=self.user1,
            question=self.question1,
            answer='答案1',
            score=85,
            is_submitted=True
        )

        CollaborativeFiltering.update_user_preferences(self.user1)

        preference = UserPreference.objects.filter(user=self.user1).first()
        self.assertIsNotNone(preference)
        self.assertEqual(preference.total_answered, 1)
        self.assertEqual(preference.avg_score, 85)


class RecommenderModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Python')
        self.question = Question.objects.create(
            title='测试问题',
            answer='测试答案',
            category=self.category,
            difficulty=1
        )

    def test_user_similarity_creation(self):
        user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

        similarity = UserSimilarity.objects.create(
            user_a=self.user,
            user_b=user2,
            similarity_score=0.85,
            common_questions=5
        )

        self.assertEqual(similarity.user_a, self.user)
        self.assertEqual(similarity.user_b, user2)
        self.assertEqual(similarity.similarity_score, 0.85)
        self.assertEqual(similarity.common_questions, 5)

    def test_question_similarity_creation(self):
        question2 = Question.objects.create(
            title='问题2',
            answer='答案2',
            category=self.category,
            difficulty=1
        )

        similarity = QuestionSimilarity.objects.create(
            question_a=self.question,
            question_b=question2,
            similarity_score=0.75,
            common_users=3
        )

        self.assertEqual(similarity.question_a, self.question)
        self.assertEqual(similarity.question_b, question2)
        self.assertEqual(similarity.similarity_score, 0.75)
        self.assertEqual(similarity.common_users, 3)

    def test_recommendation_creation(self):
        recommendation = Recommendation.objects.create(
            user=self.user,
            question=self.question,
            recommendation_type='hybrid',
            score=0.9,
            reason='测试推荐理由'
        )

        self.assertEqual(recommendation.user, self.user)
        self.assertEqual(recommendation.question, self.question)
        self.assertEqual(recommendation.recommendation_type, 'hybrid')
        self.assertEqual(recommendation.score, 0.9)
        self.assertEqual(recommendation.reason, '测试推荐理由')
        self.assertFalse(recommendation.is_viewed)
        self.assertFalse(recommendation.is_answered)

    def test_user_preference_creation(self):
        preference = UserPreference.objects.create(
            user=self.user,
            preferred_categories={'Python': {'avg_score': 85, 'count': 10}},
            preferred_difficulty={'1': {'avg_score': 80, 'count': 5}},
            weak_areas=['Java'],
            strong_areas=['Python'],
            avg_score=82.5,
            total_answered=15
        )

        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.avg_score, 82.5)
        self.assertEqual(preference.total_answered, 15)
        self.assertIn('Python', preference.strong_areas)
        self.assertIn('Java', preference.weak_areas)
