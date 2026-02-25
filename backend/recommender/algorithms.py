from collections import defaultdict
from typing import List, Tuple, Dict, Optional, Any
from django.db.models import Avg, Count, Q
from practice.models import Interaction
from .models import UserSimilarity, QuestionSimilarity, Recommendation, UserPreference
from questions.models import Question
from users.models import User
import math
import logging

logger = logging.getLogger(__name__)


class CollaborativeFiltering:
    """
    协同过滤推荐算法类
    包含基于用户和基于物品的协同过滤算法
    """

    @staticmethod
    def calculate_user_similarity(
        user_a: User,
        user_b: User,
        min_common_questions: int = 2
    ) -> float:
        """
        计算两个用户之间的相似度（基于余弦相似度）

        Args:
            user_a: 用户 A
            user_b: 用户 B
            min_common_questions: 最小共同答题数量，低于此值返回 0

        Returns:
            float: 相似度分数 (0-1)

        Raises:
            ValueError: 当用户参数无效时

        Examples:
            >>> similarity = CollaborativeFiltering.calculate_user_similarity(user1, user2)
            >>> print(similarity)
            0.85
        """
        logger.info(f"Calculating similarity between user {user_a.id} and {user_b.id}")
        
        # 获取两个用户的答题记录
        interactions_a = Interaction.objects.filter(
            user=user_a,
            score__isnull=False,
            is_submitted=True
        ).values('question', 'score')

        interactions_b = Interaction.objects.filter(
            user=user_b,
            score__isnull=False,
            is_submitted=True
        ).values('question', 'score')

        # 构建用户-题目评分字典
        ratings_a = {item['question']: item['score'] for item in interactions_a}
        ratings_b = {item['question']: item['score'] for item in interactions_b}

        # 找出共同答题的题目
        common_questions = set(ratings_a.keys()) & set(ratings_b.keys())

        if len(common_questions) < min_common_questions:
            logger.debug(f"Insufficient common questions: {len(common_questions)}")
            return 0.0

        # 计算平均评分
        avg_a = sum(ratings_a.values()) / len(ratings_a) if ratings_a else 0
        avg_b = sum(ratings_b.values()) / len(ratings_b) if ratings_b else 0

        # 计算余弦相似度
        numerator = 0
        denominator_a = 0
        denominator_b = 0

        for question_id in common_questions:
            diff_a = ratings_a[question_id] - avg_a
            diff_b = ratings_b[question_id] - avg_b

            numerator += diff_a * diff_b
            denominator_a += diff_a ** 2
            denominator_b += diff_b ** 2

        denominator = math.sqrt(denominator_a) * math.sqrt(denominator_b)

        if denominator == 0:
            logger.debug("Denominator is zero, returning 0.0")
            return 0.0

        similarity = numerator / denominator

        # 将相似度映射到 [0, 1] 范围
        similarity = (similarity + 1) / 2

        logger.info(f"Similarity calculated: {similarity:.4f}")
        return similarity

    @staticmethod
    def update_user_similarities(
        target_user: Optional[User] = None,
        min_common_questions: int = 2
    ) -> int:
        """
        更新用户相似度矩阵

        Args:
            target_user: 如果指定，只更新该用户与其他用户的相似度
            min_common_questions: 最小共同答题数量

        Returns:
            int: 更新的记录数
        """
        logger.info(f"Updating user similarities for target_user: {target_user.id if target_user else 'all'}")
        
        # 获取所有有答题记录的用户
        users_with_interactions = User.objects.filter(
            interaction__isnull=False
        ).distinct()

        if target_user:
            users_with_interactions = users_with_interactions.filter(
                Q(id=target_user.id) | Q(interaction__question__interaction__user=target_user)
            ).distinct()

        users_list = list(users_with_interactions)
        updated_count = 0

        for i, user_a in enumerate(users_list):
            for user_b in users_list[i+1:]:
                # 跳过同一用户
                if user_a.id == user_b.id:
                    continue

                # 如果指定了目标用户，只计算与目标用户的相似度
                if target_user and user_a.id != target_user.id and user_b.id != target_user.id:
                    continue

                # 计算相似度
                similarity = CollaborativeFiltering.calculate_user_similarity(
                    user_a, user_b, min_common_questions
                )

                # 获取共同答题数量
                common_questions_count = Interaction.objects.filter(
                    user=user_a,
                    score__isnull=False
                ).filter(
                    question__interaction__user=user_b,
                    question__interaction__score__isnull=False
                ).distinct().count()

                # 更新或创建相似度记录
                UserSimilarity.objects.update_or_create(
                    user_a=user_a,
                    user_b=user_b,
                    defaults={
                        'similarity_score': similarity,
                        'common_questions': common_questions_count
                    }
                )
                updated_count += 1

        return updated_count

    @staticmethod
    def calculate_question_similarity(
        question_a: Question,
        question_b: Question,
        min_common_users: int = 2
    ) -> float:
        """
        计算两个题目之间的相似度（基于用户评分）

        Args:
            question_a: 题目 A
            question_b: 题目 B
            min_common_users: 最小共同答题用户数，低于此值返回 0

        Returns:
            float: 相似度分数 (0-1)
        """
        logger.info(f"Calculating similarity between question {question_a.id} and {question_b.id}")
        
        # 获取两个题目的答题记录
        interactions_a = Interaction.objects.filter(
            question=question_a,
            score__isnull=False,
            is_submitted=True
        ).values('user', 'score')

        interactions_b = Interaction.objects.filter(
            question=question_b,
            score__isnull=False,
            is_submitted=True
        ).values('user', 'score')

        # 构建题目-用户评分字典
        ratings_a = {item['user']: item['score'] for item in interactions_a}
        ratings_b = {item['user']: item['score'] for item in interactions_b}

        # 找出共同答题的用户
        common_users = set(ratings_a.keys()) & set(ratings_b.keys())

        if len(common_users) < min_common_users:
            logger.debug(f"Insufficient common users: {len(common_users)}")
            return 0.0

        # 计算平均评分
        avg_a = sum(ratings_a.values()) / len(ratings_a) if ratings_a else 0
        avg_b = sum(ratings_b.values()) / len(ratings_b) if ratings_b else 0

        # 计算余弦相似度
        numerator = 0
        denominator_a = 0
        denominator_b = 0

        for user_id in common_users:
            diff_a = ratings_a[user_id] - avg_a
            diff_b = ratings_b[user_id] - avg_b

            numerator += diff_a * diff_b
            denominator_a += diff_a ** 2
            denominator_b += diff_b ** 2

        denominator = math.sqrt(denominator_a) * math.sqrt(denominator_b)

        if denominator == 0:
            return 0.0

        similarity = numerator / denominator

        # 将相似度映射到 [0, 1] 范围
        similarity = (similarity + 1) / 2

        return similarity

    @staticmethod
    def update_question_similarities(
        target_question: Optional[Question] = None,
        min_common_users: int = 2
    ) -> int:
        """
        更新题目相似度矩阵

        Args:
            target_question: 如果指定，只更新该题目与其他题目的相似度
            min_common_users: 最小共同答题用户数

        Returns:
            int: 更新的记录数
        """
        logger.info(f"Updating question similarities for target_question: {target_question.id if target_question else 'all'}")
        
        # 获取所有有答题记录的题目
        questions_with_interactions = Question.objects.filter(
            interaction__isnull=False,
            is_approved=True
        ).distinct()

        if target_question:
            questions_with_interactions = questions_with_interactions.filter(
                Q(id=target_question.id) | Q(interaction__user__interaction__question=target_question)
            ).distinct()

        questions_list = list(questions_with_interactions)
        updated_count = 0

        for i, question_a in enumerate(questions_list):
            for question_b in questions_list[i+1:]:
                # 跳过同一题目
                if question_a.id == question_b.id:
                    continue

                # 如果指定了目标题目，只计算与目标题目的相似度
                if target_question and question_a.id != target_question.id and question_b.id != target_question.id:
                    continue

                # 计算相似度
                similarity = CollaborativeFiltering.calculate_question_similarity(
                    question_a, question_b, min_common_users
                )

                # 获取共同答题用户数量
                common_users_count = Interaction.objects.filter(
                    question=question_a,
                    score__isnull=False
                ).filter(
                    user__interaction__question=question_b,
                    user__interaction__score__isnull=False
                ).distinct().count()

                # 更新或创建相似度记录
                QuestionSimilarity.objects.update_or_create(
                    question_a=question_a,
                    question_b=question_b,
                    defaults={
                        'similarity_score': similarity,
                        'common_users': common_users_count
                    }
                )
                updated_count += 1

        logger.info(f"Updated {updated_count} question similarities")
        return updated_count

    @staticmethod
    def user_based_recommend(
        user: User,
        n: int = 10,
        min_similarity: float = 0.1
    ) -> List[Tuple[Question, float, str]]:
        """
        基于用户的协同过滤推荐
        
        Args:
            user: 目标用户
            n: 推荐题目数量
            min_similarity: 最小相似度阈值
        
        Returns:
            list: 推荐的题目列表 [(question, score, reason), ...]
        """
        logger.info(f"Generating user-based recommendations for user {user.id}")
        
        # 获取用户已答题目
        answered_questions = set(
            Interaction.objects.filter(
                user=user,
                is_submitted=True
            ).values_list('question_id', flat=True)
        )
        
        # 冷启动处理：如果用户答题数少于3个，使用热门题目推荐
        if len(answered_questions) < 3:
            logger.info(f"User {user.id} has insufficient data, using popular questions")
            return CollaborativeFiltering._popular_questions_recommend(user, n, answered_questions)
        
        # 获取相似用户
        similar_users = UserSimilarity.objects.filter(
            Q(user_a=user) | Q(user_b=user),
            similarity_score__gte=min_similarity
        ).order_by('-similarity_score')
        
        # 如果没有相似用户，使用热门题目
        if not similar_users.exists():
            logger.info(f"No similar users found for user {user.id}, using popular questions")
            return CollaborativeFiltering._popular_questions_recommend(user, n, answered_questions)
        
        recommendations = defaultdict(float)
        reasons = defaultdict(list)
        
        for sim in similar_users:
            # 确定相似用户
            similar_user = sim.user_b if sim.user_a == user else sim.user_a
            
            # 获取相似用户的答题记录（只考虑高分题目）
            similar_user_interactions = Interaction.objects.filter(
                user=similar_user,
                score__isnull=False,
                is_submitted=True,
                score__gte=60
            ).exclude(question_id__in=answered_questions).select_related('question')
            
            for interaction in similar_user_interactions:
                question_id = interaction.question_id
                score = interaction.score
                
                # 计算推荐分数：相似度 * 用户评分
                rec_score = sim.similarity_score * (score / 100)
                
                recommendations[question_id] += rec_score
                reasons[question_id].append(
                    f"相似用户 {similar_user.username} 得分 {score}"
                )
        
        # 如果没有推荐结果，使用热门题目
        if not recommendations:
            logger.info(f"No recommendations generated for user {user.id}, using popular questions")
            return CollaborativeFiltering._popular_questions_recommend(user, n, answered_questions)
        
        # 排序并返回前 n 个推荐
        sorted_recommendations = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
        
        # 构建推荐结果
        result = []
        for question_id, score in sorted_recommendations:
            question = Question.objects.get(id=question_id)
            reason = "、".join(reasons[question_id])
            result.append((question, score, reason))
        
        return result
    
    @staticmethod
    def _popular_questions_recommend(
        user: User,
        n: int,
        answered_questions: set
    ) -> List[Tuple[Question, float, str]]:
        """
        热门题目推荐（用于冷启动）
        """
        popular_questions = Question.objects.filter(
            is_approved=True,
            is_public=True
        ).exclude(id__in=answered_questions).annotate(
            answer_count=Count('interactions')
        ).order_by('-answer_count', '-view_count')[:n]
        
        result = []
        for question in popular_questions:
            result.append((
                question,
                0.5,
                f"热门题目（{question.answer_count}人已答）"
            ))
        
        return result

    @staticmethod
    def item_based_recommend(
        user: User,
        n: int = 10,
        min_similarity: float = 0.1
    ) -> List[Tuple[Question, float, str]]:
        """
        基于物品的协同过滤推荐

        Args:
            user: 目标用户
            n: 推荐题目数量
            min_similarity: 最小相似度阈值

        Returns:
            list: 推荐的题目列表 [(question, score, reason), ...]
        """
        logger.info(f"Generating item-based recommendations for user {user.id}")
        
        # 获取用户已答题目及评分
        user_interactions = Interaction.objects.filter(
            user=user,
            score__isnull=False,
            is_submitted=True
        )

        answered_questions = {item.question_id: item.score for item in user_interactions}

        recommendations = defaultdict(float)
        reasons = defaultdict(list)

        # 对用户已答的每个题目，找到相似题目
        for question_id, user_score in answered_questions.items():
            # 获取相似题目
            similar_questions = QuestionSimilarity.objects.filter(
                Q(question_a_id=question_id) | Q(question_b_id=question_id),
                similarity_score__gte=min_similarity
            ).order_by('-similarity_score')

            for sim in similar_questions:
                # 确定相似题目
                similar_question_id = sim.question_b_id if sim.question_a_id == question_id else sim.question_a_id

                # 跳过已答题目
                if similar_question_id in answered_questions:
                    continue

                # 计算推荐分数：相似度 * 用户对该题目的评分
                rec_score = sim.similarity_score * (user_score / 100)

                recommendations[similar_question_id] += rec_score
                reasons[similar_question_id].append(
                    f"与已答题 Q{question_id} 相似度 {sim.similarity_score:.2f}"
                )

        # 排序并返回前 n 个推荐
        sorted_recommendations = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]

        # 构建推荐结果
        result = []
        for question_id, score in sorted_recommendations:
            question = Question.objects.get(id=question_id)
            reason = "、".join(reasons[question_id])
            result.append((question, score, reason))

        logger.info(f"Generated {len(result)} item-based recommendations")
        return result

    @staticmethod
    def hybrid_recommend(
        user: User,
        n: int = 10,
        user_weight: float = 0.5,
        item_weight: float = 0.5
    ) -> List[Tuple[Question, float, str]]:
        """
        混合推荐算法（结合基于用户和基于物品的推荐）

        Args:
            user: 目标用户
            n: 推荐题目数量
            user_weight: 基于用户的推荐权重
            item_weight: 基于物品的推荐权重

        Returns:
            list: 推荐的题目列表 [(question, score, reason), ...]
        """
        logger.info(f"Generating hybrid recommendations for user {user.id}")
        
        # 获取两种推荐结果
        user_based = CollaborativeFiltering.user_based_recommend(user, n * 2)
        item_based = CollaborativeFiltering.item_based_recommend(user, n * 2)

        # 合并推荐结果
        combined = defaultdict(float)
        reasons = defaultdict(list)

        # 添加基于用户的推荐
        for question, score, reason in user_based:
            combined[question.id] += score * user_weight
            reasons[question.id].append(f"用户推荐: {reason}")

        # 添加基于物品的推荐
        for question, score, reason in item_based:
            combined[question.id] += score * item_weight
            reasons[question.id].append(f"物品推荐: {reason}")

        # 排序并返回前 n 个推荐
        sorted_recommendations = sorted(
            combined.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]

        # 构建推荐结果
        result = []
        for question_id, score in sorted_recommendations:
            question = Question.objects.get(id=question_id)
            reason = "; ".join(reasons[question_id])
            result.append((question, score, reason))

        return result

    @staticmethod
    def update_user_preferences(user):
        """
        更新用户偏好分析

        Args:
            user: 目标用户
        """
        # 获取用户答题记录
        interactions = Interaction.objects.filter(
            user=user,
            score__isnull=False,
            is_submitted=True
        )

        if not interactions.exists():
            return

        # 计算平均分数
        avg_score = interactions.aggregate(avg=Avg('score'))['avg'] or 0
        total_answered = interactions.count()

        # 计算分类偏好
        category_stats = interactions.values('question__category__name').annotate(
            avg_score=Avg('score'),
            count=Count('id')
        )

        preferred_categories = {}
        weak_areas = []
        strong_areas = []

        for stat in category_stats:
            category_name = stat['question__category__name']
            if category_name:
                preferred_categories[category_name] = {
                    'avg_score': stat['avg_score'],
                    'count': stat['count'],
                    'weight': stat['avg_score'] / 100
                }

                # 判断强弱项
                if stat['avg_score'] < 60:
                    weak_areas.append(category_name)
                elif stat['avg_score'] >= 80:
                    strong_areas.append(category_name)

        # 计算难度偏好
        difficulty_stats = interactions.values('question__difficulty').annotate(
            avg_score=Avg('score'),
            count=Count('id')
        )

        preferred_difficulty = {}
        for stat in difficulty_stats:
            difficulty = stat['question__difficulty']
            preferred_difficulty[str(difficulty)] = {
                'avg_score': stat['avg_score'],
                'count': stat['count'],
                'weight': stat['avg_score'] / 100
            }

        # 更新或创建用户偏好
        UserPreference.objects.update_or_create(
            user=user,
            defaults={
                'preferred_categories': preferred_categories,
                'preferred_difficulty': preferred_difficulty,
                'weak_areas': weak_areas,
                'strong_areas': strong_areas,
                'avg_score': avg_score,
                'total_answered': total_answered
            }
        )
