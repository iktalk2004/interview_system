from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Interaction
from .serializers import InteractionSerializer
from questions.models import Question
from sentence_transformers import SentenceTransformer, util
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import math
import re
from django.core.cache import cache
from rest_framework import status
import requests
import os
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from scoring.models import ScoringHistory

# 全局加载模型（节省资源）
model = SentenceTransformer(
    'DMetaSoul/sbert-chinese-general-v2')  # 轻量级英文模型；如需中文，用 'paraphrase-multilingual-MiniLM-L12-v2'


class InteractionViewSet(viewsets.ModelViewSet):
    serializer_class = InteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['question']  # 允许按题目过滤

    def get_queryset(self):
        queryset = Interaction.objects.filter(user=self.request.user)

        question_id = self.request.query_params.get('question', None)
        if question_id is not None:
            queryset = queryset.filter(question_id=question_id)

        # 处理 question__in 参数过滤（多个题目ID）
        question_in = self.request.query_params.get('question__in', None)
        if question_in is not None:
            question_ids = [int(i) for i in question_in.split(',') if i.isdigit()]
            if question_ids:
                queryset = queryset.filter(question_id__in=question_ids)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="获取当前用户的答题历史记录",
        responses={200: InteractionSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def history(self, request):
        interactions = self.get_queryset().order_by('-created_at')
        return Response(self.get_serializer(interactions, many=True).data)

    @swagger_auto_schema(
        operation_description="收藏或取消收藏题目",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'is_favorite': openapi.Schema(type=openapi.TYPE_BOOLEAN)})}
    )
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        interaction = self.get_object()
        interaction.is_favorite = not interaction.is_favorite
        interaction.save()
        return Response({'is_favorite': interaction.is_favorite})

    @swagger_auto_schema(
        operation_description="重置交互状态，允许重新答题",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING), 'status': openapi.Schema(type=openapi.TYPE_STRING), 'score': openapi.Schema(type=openapi.TYPE_NUMBER)})}
    )
    @action(detail=True, methods=['post'])
    def reset_interaction(self, request, pk=None):
        interaction = self.get_object()
        interaction.score = None
        interaction.answer = ''
        interaction.is_submitted = False
        interaction.status = 'draft'
        interaction.save()
        return Response({
            'message': '重置成功，您可以重新答题',
            'status': interaction.status,
            'score': interaction.score
        })

    @swagger_auto_schema(
        operation_description="使用嵌入模型计算答案分数",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'score': openapi.Schema(type=openapi.TYPE_NUMBER)})}
    )
    @action(detail=True, methods=['post'])
    def embedding_score(self, request, pk=None):

        interaction = self.get_object()
        if not interaction.answer:
            return Response({'error': '请先提交答案'}, status=status.HTTP_400_BAD_REQUEST)
        question = interaction.question
        if not question.answer:
            return Response({'error': '该题目无标准答案'}, status=status.HTTP_400_BAD_REQUEST)

        # 增强预处理：去除标点、规范化空格、转小写（处理中文/英文混杂）
        def preprocess(text):
            text = re.sub(r'[^\u4e00-\u9fa5\w\s]', '', text)  # 保留中文、字母、数字、空格
            text = ' '.join(text.split())  # 规范化空格
            return text.lower()

        user_answer = preprocess(interaction.answer)
        std_answer = preprocess(question.answer)

        # 最小长度检查：如果用户答案太短（<标准50%），直接低分
        if len(user_answer) < 0.5 * len(std_answer):
            score = 0.0
            interaction.score = score
            interaction.save()
            return Response({'score': score, 'feedback': '答案过短，缺少关键内容'})

        # 缓存标准答案嵌入
        cache_key = f'question_embedding_{question.id}'
        std_embedding = cache.get(cache_key)
        if std_embedding is None:
            std_embedding = model.encode(std_answer)
            cache.set(cache_key, std_embedding, timeout=86400)  # 24小时

        # 用户嵌入
        user_embedding = model.encode(user_answer)

        # 余弦相似度
        cos_sim = util.cos_sim(user_embedding, std_embedding)[0][0].item()

        # 长度惩罚（柔和版）
        len_penalty = max(0.5, 1 - abs(len(user_answer) - len(std_answer)) / max(len(user_answer), len(std_answer),
                                                                                 1))  # 最小0.5，避免过度惩罚

        # 调整相似度
        adjusted_sim = cos_sim * len_penalty

        # 非线性映射：sigmoid，更宽容（阈值0.5，陡度6）
        if adjusted_sim < 0.3:  # 最小阈值，避免无关答案高分
            sigmoid_score = 0
        else:
            sigmoid_score = 1 / (1 + math.exp(-6 * (adjusted_sim - 0.5)))

        # 现有嵌入模型分数（0-100）
        embedding_score = round(max(0, min(100, sigmoid_score * 100)), 1)
        if embedding_score >= 95:
            embedding_score = 100

        details = {
            'cosine_similarity': float(cos_sim),
            'length_penalty': float(len_penalty),
            'adjusted_similarity': float(adjusted_sim),
            'sigmoid_score': float(sigmoid_score)
        }

        interaction.score = embedding_score
        interaction.save()

        ScoringHistory.objects.create(
            interaction=interaction,
            scoring_method='embedding',
            score=embedding_score,
            details=details
        )

        return Response({'score': embedding_score})

    @swagger_auto_schema(
        operation_description="使用DeepSeek API计算答案分数",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'score': openapi.Schema(type=openapi.TYPE_NUMBER)})}
    )
    @action(detail=True, methods=['post'])
    def deepseek_score(self, request, pk=None):
        interaction = self.get_object()
        if not interaction.answer:
            return Response({'error': '请先提交答案'}, status=status.HTTP_400_BAD_REQUEST)
        question = interaction.question
        if not question.answer:
            return Response({'error': '该题目无标准答案'}, status=status.HTTP_400_BAD_REQUEST)

        # 使用DeepSeek API进行LLM评分
        try:
            # 构建DeepSeek API请求
            prompt = f"""
            你是一个严格的评分助手。请评估用户答案的分数。
            问题：{question.title}
            用户答案：{interaction.answer}
            - 分数范围：0-100，满分100表示完美匹配。
            只输出分数（整数），不要添加任何解释。
            """

            # 从环境变量获取 DeepSeek API 密钥
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                return Response({'error': '未配置 DeepSeek API 密钥'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # DeepSeek API端点
            api_url = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/chat/completions')

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 10,
                "temperature": 0.0,
                "stream": False
            }

            response = requests.post(api_url, headers=headers, json=data)

            if response.status_code == 200:
                response_data = response.json()
                llm_output = response_data["choices"][0]["message"]["content"].strip()

                # 解析分数
                llm_score = float(re.search(r'\d+', llm_output).group())
                llm_score = max(0, min(100, llm_score))

                if llm_score >= 95:
                    llm_score = 100

                details = {
                    'llm_output': llm_output,
                    'model': 'deepseek-chat'
                }

                interaction.score = llm_score
                interaction.save()

                ScoringHistory.objects.create(
                    interaction=interaction,
                    scoring_method='llm',
                    score=llm_score,
                    details=details
                )

                return Response({'score': llm_score})
            else:
                return Response({'error': '评分请求失败'}, status=response.status_code)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
