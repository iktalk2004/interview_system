from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ScoringHistory
from .serializers import ScoringHistorySerializer
from practice.models import Interaction
from questions.models import Question
from sentence_transformers import SentenceTransformer, util
from django.core.cache import cache
import math
import re
import requests
import os


class ScoringViewSet(viewsets.ModelViewSet):
    """
    评分视图集
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
        scoring_history = self.get_object()
        interaction = scoring_history.interaction

        if not interaction.answer:
            return Response({'error': '请先提交答案'}, status=status.HTTP_400_BAD_REQUEST)

        question = interaction.question
        if not question.answer:
            return Response({'error': '该题目无标准答案'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 全局加载模型（节省资源）
            model = SentenceTransformer('DMetaSoul/sbert-chinese-general-v2')

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
                details = {
                    'reason': '答案过短，缺少关键内容',
                    'user_answer_length': len(user_answer),
                    'std_answer_length': len(std_answer)
                }

                # 保存评分历史
                ScoringHistory.objects.create(
                    interaction=interaction,
                    scoring_method='embedding',
                    score=score,
                    details=details
                )

                return Response({'score': score, 'details': details})

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
            len_penalty = max(0.5, 1 - abs(len(user_answer) - len(std_answer)) / max(len(user_answer), len(std_answer), 1))

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

            # 保存评分历史
            ScoringHistory.objects.create(
                interaction=interaction,
                scoring_method='embedding',
                score=embedding_score,
                details=details
            )

            # 更新 interaction 的分数
            interaction.score = embedding_score
            interaction.save()

            return Response({'score': embedding_score, 'details': details})

        except Exception as e:
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
                llm_score = max(0, min(100, llm_score))  # 限制分数在0-100范围内

                if llm_score >= 95:
                    llm_score = 100

                details = {
                    'llm_output': llm_output,
                    'model': 'deepseek-chat'
                }

                # 保存评分历史
                ScoringHistory.objects.create(
                    interaction=interaction,
                    scoring_method='llm',
                    score=llm_score,
                    details=details
                )

                # 更新 interaction 的分数
                interaction.score = llm_score
                interaction.save()

                return Response({'score': llm_score, 'details': details})
            else:
                return Response({'error': '评分请求失败'}, status=response.status_code)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def score_interaction(self, request):
        """
        对指定的交互进行评分
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

            # 创建评分历史记录
            scoring_history = ScoringHistory.objects.create(
                interaction=interaction,
                scoring_method=method,
                score=0  # 初始分数，后续更新
            )

            # 根据方法调用相应的评分函数
            if method == 'embedding':
                return self.embedding_score(request, pk=scoring_history.pk)
            elif method == 'llm':
                return self.llm_score(request, pk=scoring_history.pk)
            else:
                return Response({'error': '不支持的评分方法'}, status=status.HTTP_400_BAD_REQUEST)

        except Interaction.DoesNotExist:
            return Response({'error': '交互记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
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
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
