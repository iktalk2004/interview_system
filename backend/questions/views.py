from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Question
from .serializers import CategorySerializer, QuestionSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # 读公开，写需登录


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_approved', 'difficult']
    search_fields = ['title', 'answer']  # 内部搜索字段
    ordering_fields = ['created_at', 'difficulty']

    def perform_create(self, serializer):
        # 创建时添加创建者
        serializer.save(creator=self.request.user)
