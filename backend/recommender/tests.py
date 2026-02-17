from django.test import TestCase
from django.contrib.auth import get_user_model
from .algorithms import CollaborativeFiltering
from .models import UserSimilarity, QuestionSimilarity
from practice.models import Interaction
from questions.models import Question, Category

User = get_user_model()


class CollaborativeFilteringTestCase(TestCase):
    """
    协同过滤算法测试用例
    """

    def setUp(self):
        # 创建测试用户
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user3 = User.objects.create_user(username='user3', password='pass')

        # 创建测试分类
        self.category = Category.objects.create(name='Python')

        # 创建测试题目
        self.question1 = Question.objects.create(
            title='Python 基础',
            category=self.category,
            difficulty=1,
            is_approved=True
        )
        self.question2 = Question.objects.create(
            title='Python 进阶',
            category=self.category,
            difficulty=2,
            is_approved=True
        )
        self.question3 = Question.objects.create(
            title='Python 高级',
            category=self.category,
            difficulty=3,
            is_approved=True
        )

        # 创建测试交互记录
        Interaction.objects.create(
            user=self.user1,
            question=self.question1,
            score=90,
            is_submitted=True
        )
        Interaction.objects.create(
            user=self.user1,
            question=self.question2,
            score=80,
            is_submitted=True
        )
        Interaction.objects.create(
            user=self.user2,
            question=self.question1,
            score=85,
            is_submitted=True
        )
        Interaction.objects.create(
            user=self.user2,
            question=self.question3,
            score=70,
            is_submitted=True
        )

    def test_calculate_user_similarity(self):
        """
        测试用户相似度计算
        """
        similarity = CollaborativeFiltering.calculate_user_similarity(
            self.user1, self.user2, min_common_questions=1
        )

        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    def test_update_user_similarities(self):
        """
        测试更新用户相似度矩阵
        """
        updated_count = CollaborativeFiltering.update_user_similarities()

        self.assertGreater(updated_count, 0)

        # 验证相似度记录已创建
        similarity = UserSimilarity.objects.filter(
            user_a=self.user1,
            user_b=self.user2
        ).first()

        self.assertIsNotNone(similarity)
        self.assertGreater(similarity.similarity_score, 0)

    def test_user_based_recommend(self):
        """
        测试基于用户的推荐
        """
        # 先更新相似度矩阵
        CollaborativeFiltering.update_user_similarities()

        # 为 user3 生成推荐
        recommendations = CollaborativeFiltering.user_based_recommend(
            self.user3, n=5, min_similarity=0.0
        )

        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)

        if recommendations:
            question, score, reason = recommendations[0]
            self.assertIsInstance(question, Question)
            self.assertIsInstance(score, float)
            self.assertIsInstance(reason, str)

    def test_item_based_recommend(self):
        """
        测试基于物品的推荐
        """
        # 先更新相似度矩阵
        CollaborativeFiltering.update_question_similarities()

        # 为 user3 生成推荐
        recommendations = CollaborativeFiltering.item_based_recommend(
            self.user3, n=5, min_similarity=0.0
        )

        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)

        if recommendations:
            question, score, reason = recommendations[0]
            self.assertIsInstance(question, Question)
            self.assertIsInstance(score, float)
            self.assertIsInstance(reason, str)

    def test_hybrid_recommend(self):
        """
        测试混合推荐
        """
        # 先更新相似度矩阵
        CollaborativeFiltering.update_user_similarities()
        CollaborativeFiltering.update_question_similarities()

        # 为 user3 生成推荐
        recommendations = CollaborativeFiltering.hybrid_recommend(
            self.user3, n=5
        )

        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)

        if recommendations:
            question, score, reason = recommendations[0]
            self.assertIsInstance(question, Question)
            self.assertIsInstance(score, float)
            self.assertIsInstance(reason, str)

    def test_calculate_question_similarity(self):
        """
        测试题目相似度计算
        """
        similarity = CollaborativeFiltering.calculate_question_similarity(
            self.question1, self.question2, min_common_users=1
        )

        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    def test_update_question_similarities(self):
        """
        测试更新题目相似度矩阵
        """
        updated_count = CollaborativeFiltering.update_question_similarities()

        self.assertGreater(updated_count, 0)

        # 验证相似度记录已创建
        similarity = QuestionSimilarity.objects.filter(
            question_a=self.question1,
            question_b=self.question2
        ).first()

        self.assertIsNotNone(similarity)
        self.assertGreater(similarity.similarity_score, 0)
