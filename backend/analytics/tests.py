from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from questions.models import Question, Category
from practice.models import Interaction
from analytics.models import UserDailyStats, UserPerformanceTrend, UserScoreDistribution

User = get_user_model()


class AnalyticsModelsTest(TestCase):
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

    def test_user_daily_stats_creation(self):
        today = timezone.now().date()
        stats = UserDailyStats.objects.create(
            user=self.user,
            date=today,
            questions_viewed=10,
            questions_answered=5,
            total_score=425,
            avg_score=85.0,
            time_spent=300
        )

        self.assertEqual(stats.user, self.user)
        self.assertEqual(stats.date, today)
        self.assertEqual(stats.questions_viewed, 10)
        self.assertEqual(stats.questions_answered, 5)
        self.assertEqual(stats.total_score, 425)
        self.assertEqual(stats.avg_score, 85.0)
        self.assertEqual(stats.time_spent, 300)

    def test_user_performance_trend_creation(self):
        trend = UserPerformanceTrend.objects.create(
            user=self.user,
            period='weekly',
            start_date=timezone.now().date() - timedelta(days=7),
            end_date=timezone.now().date(),
            total_answered=20,
            avg_score=82.5,
            best_score=95,
            worst_score=60,
            improvement_rate=5.2
        )

        self.assertEqual(trend.user, self.user)
        self.assertEqual(trend.period, 'weekly')
        self.assertEqual(trend.total_answered, 20)
        self.assertEqual(trend.avg_score, 82.5)
        self.assertEqual(trend.best_score, 95)
        self.assertEqual(trend.worst_score, 60)
        self.assertEqual(trend.improvement_rate, 5.2)

    def test_user_score_distribution_creation(self):
        distribution = UserScoreDistribution.objects.create(
            user=self.user,
            score_range='80-89',
            count=15,
            percentage=50.0
        )

        self.assertEqual(distribution.user, self.user)
        self.assertEqual(distribution.score_range, '80-89')
        self.assertEqual(distribution.count, 15)
        self.assertEqual(distribution.percentage, 50.0)

    def test_daily_stats_str_representation(self):
        today = timezone.now().date()
        stats = UserDailyStats.objects.create(
            user=self.user,
            date=today,
            questions_viewed=10,
            questions_answered=5,
            total_score=425,
            avg_score=85.0,
            time_spent=300
        )

        expected_str = f"{self.user.username} - {today}"
        self.assertEqual(str(stats), expected_str)

    def test_performance_trend_str_representation(self):
        trend = UserPerformanceTrend.objects.create(
            user=self.user,
            period='weekly',
            start_date=timezone.now().date() - timedelta(days=7),
            end_date=timezone.now().date(),
            total_answered=20,
            avg_score=82.5,
            best_score=95,
            worst_score=60,
            improvement_rate=5.2
        )

        expected_str = f"{self.user.username} - weekly"
        self.assertEqual(str(trend), expected_str)

    def test_score_distribution_str_representation(self):
        distribution = UserScoreDistribution.objects.create(
            user=self.user,
            score_range='80-89',
            count=15,
            percentage=50.0
        )

        expected_str = f"{self.user.username} - 80-89"
        self.assertEqual(str(distribution), expected_str)

    def test_unique_daily_stats(self):
        today = timezone.now().date()
        UserDailyStats.objects.create(
            user=self.user,
            date=today,
            questions_viewed=10,
            questions_answered=5,
            total_score=425,
            avg_score=85.0,
            time_spent=300
        )

        with self.assertRaises(Exception):
            UserDailyStats.objects.create(
                user=self.user,
                date=today,
                questions_viewed=5,
                questions_answered=2,
                total_score=200,
                avg_score=80.0,
                time_spent=150
            )

    def test_daily_stats_calculation(self):
        today = timezone.now().date()
        Interaction.objects.create(
            user=self.user,
            question=self.question,
            answer='测试答案',
            score=85,
            is_submitted=True
        )

        stats = UserDailyStats.objects.create(
            user=self.user,
            date=today,
            questions_viewed=1,
            questions_answered=1,
            total_score=85,
            avg_score=85.0,
            time_spent=60
        )

        self.assertEqual(stats.questions_answered, 1)
        self.assertEqual(stats.avg_score, 85.0)

    def test_multiple_users_stats(self):
        user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

        today = timezone.now().date()

        stats1 = UserDailyStats.objects.create(
            user=self.user,
            date=today,
            questions_viewed=10,
            questions_answered=5,
            total_score=425,
            avg_score=85.0,
            time_spent=300
        )

        stats2 = UserDailyStats.objects.create(
            user=user2,
            date=today,
            questions_viewed=8,
            questions_answered=4,
            total_score=320,
            avg_score=80.0,
            time_spent=250
        )

        all_stats = UserDailyStats.objects.filter(date=today)
        self.assertEqual(all_stats.count(), 2)
        self.assertIn(stats1, all_stats)
        self.assertIn(stats2, all_stats)
