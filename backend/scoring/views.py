from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ScoringHistory
from .serializers import ScoringHistorySerializer
from .factory import create_scorer, ScoringStrategyFactory
from practice.models import Interaction
from questions.models import Question
import os
import logging

logger = logging.getLogger(__name__)

DISABLE_LLM_SCORING = os.getenv('DISABLE_LLM_SCORING', 'False').lower() == 'true'


class ScoringViewSet(viewsets.ModelViewSet):
    """
    评分视图集（使用策略模式）
    """
    queryset = ScoringHistory.objects.all()
    serializer_class = ScoringHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 只返回当前用户的评分历史
        queryset = queryset.filter(interaction__user=user)

        # 过滤参数
        scoring_method = self.request.query_params.get('method')
        if scoring_method:
            queryset = queryset.filter(scoring_method=scoring_method)

        interaction_id = self.request.query_params.get('interaction_id')
        if interaction_id:
            queryset = queryset.filter(interaction_id=interaction_id)

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def embedding_score(self, request, pk=None):
        """
        使用嵌入模型计算分数
        """
        # 检查是否禁用了智能评分
        if DISABLE_LLM_SCORING:
            return Response({
                'error': '智能评分功能已禁用。如需启用，请在 .env 文件中设置 DISABLE_LLM_SCORING=False',
                'score': 0,
                'disabled': True
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        scoring_history = self.get_object()
        interaction = scoring_history.interaction

        if not interaction.answer:
            return Response({'error': '请先提交答案'}, status=status.HTTP_400_BAD_REQUEST)

        question = interaction.question
        if not question.answer:
            return Response({'error': '该题目无标准答案'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 使用策略模式进行评分
            scorer = create_scorer('embedding')
            result = scorer.score(
                user_answer=interaction.answer,
                standard_answer=question.answer,
                question_id=question.id
            )

            # 保存评分历史
            ScoringHistory.objects.create(
                interaction=interaction,
                scoring_method=result['method'],
                score=result['score'],
                details=result['details']
            )

            # 更新 interaction 的分数
            interaction.score = result['score']
            interaction.scoring_method = result['method']
            interaction.save()

            return Response({
                'score': result['score'],
                'details': result['details'],
                'method': result['method']
            })

        except Exception as e:
            logger.error(f"Embedding scoring failed: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def llm_score(self, request, pk=None):
        """
        使用大语言模型（DeepSeek）计算分数
        """
        scoring_history = self.get_object()
        interaction = scoring_history.interaction

        if not interaction.answer:
            return Response({'error': '请先提交答案'}, status=status.HTTP_400_BAD_REQUEST)

        question = interaction.question
        if not question.answer:
            return Response({'error': '该题目无标准答案'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 使用策略模式进行评分
            scorer = create_scorer('llm')
            result = scorer.score(
                user_answer=interaction.answer,
                standard_answer=question.answer,
                question_title=question.title
            )

            # 保存评分历史
            ScoringHistory.objects.create(
                interaction=interaction,
                scoring_method=result['method'],
                score=result['score'],
                details=result['details']
            )

            # 更新 interaction 的分数
            interaction.score = result['score']
            interaction.scoring_method = result['method']
            interaction.save()

            return Response({
                'score': result['score'],
                'details': result['details'],
                'method': result['method']
            })

        except Exception as e:
            logger.error(f"LLM scoring failed: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def score_interaction(self, request):
        """
        对指定的交互进行评分（使用策略模式）
        参数：
        - interaction_id: 交互ID
        - method: 评分方法 (embedding, llm)
        """
        interaction_id = request.data.get('interaction_id')
        method = request.data.get('method', 'embedding')

        if not interaction_id:
            return Response({'error': '请提供 interaction_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            interaction = Interaction.objects.get(id=interaction_id, user=request.user)

            if not interaction.answer:
                return Response({'error': '请先提交答案'}, status=status.HTTP_400_BAD_REQUEST)

            question = interaction.question
            if not question.answer:
                return Response({'error': '该题目无标准答案'}, status=status.HTTP_400_BAD_REQUEST)

            # 使用策略模式进行评分
            scorer = create_scorer(method)
            result = scorer.score(
                user_answer=interaction.answer,
                standard_answer=question.answer,
                question_id=question.id,
                question_title=question.title
            )

            # 保存评分历史
            scoring_history = ScoringHistory.objects.create(
                interaction=interaction,
                scoring_method=result['method'],
                score=result['score'],
                details=result['details']
            )

            # 更新 interaction 的分数
            interaction.score = result['score']
            interaction.scoring_method = result['method']
            interaction.save()

            return Response({
                'score': result['score'],
                'details': result['details'],
                'method': result['method']
            })

        except Interaction.DoesNotExist:
            return Response({'error': '交互记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Scoring failed: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def get_latest_scores(self, request):
        """
        获取最近的评分记录
        参数：
        - limit: 返回数量，默认 10
        """
        limit = int(request.query_params.get('limit', 10))

        try:
            latest_scores = self.get_queryset()[:limit]
            serializer = self.get_serializer(latest_scores, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to get latest scores: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def list_strategies(self, request):
        """
        列出所有可用的评分策略
        """
        strategies = ScoringStrategyFactory.list_strategies()
        return Response({
            'strategies': strategies,
            'count': len(strategies)
        })
