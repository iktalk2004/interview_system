from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import UserSimilarity, QuestionSimilarity, Recommendation, UserPreference
from .serializers import (
    UserSimilaritySerializer,
    QuestionSimilaritySerializer,
    RecommendationSerializer,
    UserPreferenceSerializer
)
from .algorithms import CollaborativeFiltering
from practice.models import Interaction
from questions.models import Question


class UserSimilarityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户相似度视图集
    """
    queryset = UserSimilarity.objects.all()
    serializer_class = UserSimilaritySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 只返回与当前用户相关的相似度记录
        queryset = queryset.filter(Q(user_a=user) | Q(user_b=user))

        # 按相似度排序
        queryset = queryset.order_by('-similarity_score')

        return queryset

    @action(detail=False, methods=['post'])
    def update_similarities(self, request):
        """
        更新用户相似度矩阵
        """
        user = request.user

        try:
            updated_count = CollaborativeFiltering.update_user_similarities(
                target_user=user,
                min_common_questions=2
            )
            return Response({
                'message': f'成功更新 {updated_count} 条用户相似度记录',
                'updated_count': updated_count
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionSimilarityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    题目相似度视图集
    """
    queryset = QuestionSimilarity.objects.all()
    serializer_class = QuestionSimilaritySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        question_id = self.request.query_params.get('question_id')

        if question_id:
            # 只返回与指定题目相关的相似度记录
            queryset = queryset.filter(
                Q(question_a_id=question_id) | Q(question_b_id=question_id)
            )

        # 按相似度排序
        queryset = queryset.order_by('-similarity_score')

        return queryset

    @action(detail=False, methods=['post'])
    def update_similarities(self, request):
        """
        更新题目相似度矩阵
        """
        question_id = request.data.get('question_id')

        try:
            if question_id:
                question = Question.objects.get(id=question_id)
                updated_count = CollaborativeFiltering.update_question_similarities(
                    target_question=question,
                    min_common_users=2
                )
            else:
                updated_count = CollaborativeFiltering.update_question_similarities(
                    min_common_users=2
                )

            return Response({
                'message': f'成功更新 {updated_count} 条题目相似度记录',
                'updated_count': updated_count
            })
        except Question.DoesNotExist:
            return Response(
                {'error': '题目不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecommendationViewSet(viewsets.ModelViewSet):
    """
    推荐视图集
    """
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 只返回当前用户的推荐
        queryset = queryset.filter(user=user)

        # 过滤参数
        recommendation_type = self.request.query_params.get('type')
        if recommendation_type:
            queryset = queryset.filter(recommendation_type=recommendation_type)

        is_viewed = self.request.query_params.get('is_viewed')
        if is_viewed is not None:
            queryset = queryset.filter(is_viewed=is_viewed.lower() == 'true')

        is_answered = self.request.query_params.get('is_answered')
        if is_answered is not None:
            queryset = queryset.filter(is_answered=is_answered.lower() == 'true')

        # 按推荐分数排序
        queryset = queryset.order_by('-score', '-created_at')

        return queryset

    @action(detail=False, methods=['get'])
    def generate_recommendations(self, request):
        """
        生成推荐题目
        参数：
        - type: 推荐类型 (user_based, item_based, hybrid)
        - n: 推荐数量，默认 10
        - min_similarity: 最小相似度，默认 0.1
        """
        user = request.user
        recommendation_type = request.query_params.get('type', 'hybrid')
        n = int(request.query_params.get('n', 10))
        min_similarity = float(request.query_params.get('min_similarity', 0.1))

        try:
            if recommendation_type == 'user_based':
                recommendations = CollaborativeFiltering.user_based_recommend(
                    user, n, min_similarity
                )
            elif recommendation_type == 'item_based':
                recommendations = CollaborativeFiltering.item_based_recommend(
                    user, n, min_similarity
                )
            elif recommendation_type == 'hybrid':
                recommendations = CollaborativeFiltering.hybrid_recommend(
                    user, n
                )
            else:
                return Response(
                    {'error': '不支持的推荐类型'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 保存推荐记录
            saved_recommendations = []
            for question, score, reason in recommendations:
                rec, created = Recommendation.objects.update_or_create(
                    user=user,
                    question=question,
                    recommendation_type=recommendation_type,
                    defaults={
                        'score': score,
                        'reason': reason
                    }
                )
                saved_recommendations.append(rec)

            # 返回推荐结果
            serializer = self.get_serializer(saved_recommendations, many=True)
            return Response({
                'recommendations': serializer.data,
                'count': len(saved_recommendations),
                'type': recommendation_type
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """
        标记推荐为已查看
        """
        recommendation = self.get_object()
        recommendation.is_viewed = True
        recommendation.save()

        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_viewed(self, request):
        """
        标记所有推荐为已查看
        """
        user = request.user
        updated_count = Recommendation.objects.filter(
            user=user,
            is_viewed=False
        ).update(is_viewed=True)

        return Response({
            'message': f'成功标记 {updated_count} 条推荐为已查看',
            'updated_count': updated_count
        })

    @action(detail=False, methods=['post'])
    def clear_old_recommendations(self, request):
        """
        清除旧的推荐记录
        参数：
        - days: 保留最近几天的推荐，默认 7 天
        """
        user = request.user
        days = int(request.data.get('days', 7))

        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = Recommendation.objects.filter(
            user=user,
            created_at__lt=cutoff_date
        ).delete()[0]

        return Response({
            'message': f'成功清除 {deleted_count} 条旧推荐记录',
            'deleted_count': deleted_count
        })


class UserPreferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户偏好视图集
    """
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 只返回当前用户的偏好
        queryset = queryset.filter(user=user)

        return queryset

    @action(detail=False, methods=['post'])
    def update_preferences(self, request):
        """
        更新用户偏好分析
        """
        user = request.user

        try:
            CollaborativeFiltering.update_user_preferences(user)
            preference = UserPreference.objects.get(user=user)
            serializer = self.get_serializer(preference)
            return Response({
                'message': '用户偏好更新成功',
                'preference': serializer.data
            })
        except UserPreference.DoesNotExist:
            return Response(
                {'error': '用户偏好不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecommendationSystemViewSet(viewsets.GenericViewSet):
    """
    推荐系统管理视图集
    提供系统级别的推荐管理功能
    """
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['post'])
    def rebuild_all_similarities(self, request):
        """
        重建所有相似度矩阵
        """
        try:
            # 更新用户相似度
            user_count = CollaborativeFiltering.update_user_similarities(
                min_common_questions=2
            )

            # 更新题目相似度
            question_count = CollaborativeFiltering.update_question_similarities(
                min_common_users=2
            )

            return Response({
                'message': '成功重建所有相似度矩阵',
                'user_similarities_updated': user_count,
                'question_similarities_updated': question_count
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def update_all_user_preferences(self, request):
        """
        更新所有用户的偏好分析
        """
        try:
            from users.models import User

            users = User.objects.filter(interaction__isnull=False).distinct()
            updated_count = 0

            for user in users:
                CollaborativeFiltering.update_user_preferences(user)
                updated_count += 1

            return Response({
                'message': f'成功更新 {updated_count} 个用户的偏好分析',
                'updated_count': updated_count
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def system_stats(self, request):
        """
        获取推荐系统统计信息
        """
        try:
            stats = {
                'user_similarities': UserSimilarity.objects.count(),
                'question_similarities': QuestionSimilarity.objects.count(),
                'recommendations': Recommendation.objects.count(),
                'user_preferences': UserPreference.objects.count(),
                'users_with_interactions': User.objects.filter(
                    interaction__isnull=False
                ).distinct().count(),
                'questions_with_interactions': Question.objects.filter(
                    interaction__isnull=False
                ).distinct().count(),
            }

            return Response(stats)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
