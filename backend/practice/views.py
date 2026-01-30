from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Interaction
from .serializers import InteractionSerializer
from questions.models import Question
from sentence_transformers import SentenceTransformer, util
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# 全局加载模型（节省资源）
model = SentenceTransformer(
    'paraphrase-multilingual-MiniLM-L12-v2')  # 轻量级英文模型；如需中文，用 'paraphrase-multilingual-MiniLM-L12-v2'


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

    @action(detail=False, methods=['get'])
    def history(self, request):
        interactions = self.get_queryset().order_by('-created_at')  # 使用过滤后的queryset
        return Response(self.get_serializer(interactions, many=True).data)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        interaction = self.get_object()
        interaction.is_favorite = not interaction.is_favorite
        interaction.save()
        return Response({'is_favorite': interaction.is_favorite})

    @action(detail=True, methods=['post'])
    def score(self, request, pk=None):
        interaction = self.get_object()
        if not interaction.answer:
            return Response({'error': '请先提交答案'}, status=400)

        question = interaction.question
        if not question.answer:
            return Response({'error': '该题目无标准答案'}, status=400)

        # NLP相似度计算
        embeddings = model.encode([interaction.answer, question.answer])
        cos_sim = util.cos_sim(embeddings[0], embeddings[1])[0][0].item()  # 余弦相似度 (-1到1，通常>0)

        # 缩放到0-10分数（可调整阈值）
        score = max(0, min(10, (cos_sim + 1) / 2 * 10))  # 归一化到0-10

        interaction.score = score
        interaction.save()
        return Response({'score': score})
