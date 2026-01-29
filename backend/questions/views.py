from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Question
from .serializers import CategorySerializer, QuestionSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # 读公开，写需登录


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    #  筛选条件
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]  # 过滤、搜索、排序
    filterset_fields = ['category', 'is_approved', 'difficulty']
    search_fields = ['title', 'answer']
    ordering_fields = ['created_at', 'difficulty']

    def perform_create(self, serializer):
        # 创建时添加创建者
        serializer.save(creator=self.request.user)
