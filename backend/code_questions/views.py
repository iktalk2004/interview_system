from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, F
from .models import CodeQuestion, TestCase, CodeSubmission, CodeBookmark, CodeNote
from .serializers import (
    CodeQuestionSerializer, CodeQuestionListSerializer, CodeQuestionDetailSerializer,
    TestCaseSerializer, CodeSubmissionSerializer, CodeSubmissionCreateSerializer,
    CodeBookmarkSerializer, CodeNoteSerializer
)
from .services import CodeExecutor


class CodeQuestionViewSet(viewsets.ModelViewSet):
    """
    代码题目视图集
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = CodeQuestion.objects.filter(
            question__is_approved=True,
            is_public=True
        ).select_related('question', 'question__category')

        # 搜索过滤
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(question__title__icontains=search) |
                Q(question__explanation__icontains=search)
            )

        # 语言过滤
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)

        # 难度过滤
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(question__difficulty=difficulty)

        # 分类过滤
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(question__category_id=category)

        # 排序
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'difficulty':
            queryset = queryset.order_by('question__difficulty')
        elif ordering == '-difficulty':
            queryset = queryset.order_by('-question__difficulty')
        else:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return CodeQuestionListSerializer
        elif self.action == 'retrieve':
            return CodeQuestionDetailSerializer
        return CodeQuestionSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        """
        收藏/取消收藏题目
        """
        code_question = self.get_object()
        bookmark, created = CodeBookmark.objects.get_or_create(
            user=request.user,
            code_question=code_question
        )

        if not created:
            bookmark.delete()
            return Response({'bookmarked': False, 'message': '已取消收藏'})

        return Response({'bookmarked': True, 'message': '收藏成功'})

    @action(detail=True, methods=['get', 'post', 'put'])
    def note(self, request, pk=None):
        """
        获取/创建/更新笔记
        """
        code_question = self.get_object()

        if request.method == 'GET':
            try:
                note = CodeNote.objects.get(
                    user=request.user,
                    code_question=code_question
                )
                serializer = CodeNoteSerializer(note)
                return Response(serializer.data)
            except CodeNote.DoesNotExist:
                return Response({'content': ''})

        elif request.method == 'POST':
            serializer = CodeNoteSerializer(data={
                'user': request.user.id,
                'code_question': code_question.id,
                'content': request.data.get('content', '')
            })
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'PUT':
            try:
                note = CodeNote.objects.get(
                    user=request.user,
                    code_question=code_question
                )
                note.content = request.data.get('content', '')
                note.save()
                serializer = CodeNoteSerializer(note)
                return Response(serializer.data)
            except CodeNote.DoesNotExist:
                return Response({'error': '笔记不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        提交代码
        """
        code_question = self.get_object()
        serializer = CodeSubmissionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 创建提交记录
        submission = CodeSubmission.objects.create(
            user=request.user,
            code_question=code_question,
            code=serializer.validated_data['code'],
            language=serializer.validated_data['language'],
            total_test_cases=code_question.test_cases.count()
        )

        # 异步执行代码
        try:
            executor = CodeExecutor()
            result = executor.execute(
                code=serializer.validated_data['code'],
                language=serializer.validated_data['language'],
                test_cases=code_question.test_cases.all(),
                time_limit=code_question.time_limit,
                memory_limit=code_question.memory_limit
            )

            # 更新提交记录
            submission.status = result['status']
            submission.runtime = result.get('runtime')
            submission.memory = result.get('memory')
            submission.passed_test_cases = result.get('passed_test_cases', 0)
            submission.error_message = result.get('error_message', '')
            submission.test_case_results = result.get('test_case_results', {})
            submission.save()

            return Response(CodeSubmissionSerializer(submission).data)

        except Exception as e:
            submission.status = 'system_error'
            submission.error_message = str(e)
            submission.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def bookmarks(self, request):
        """
        获取收藏的题目列表
        """
        bookmarks = CodeBookmark.objects.filter(user=request.user).select_related(
            'code_question', 'code_question__question', 'code_question__question__category'
        )

        code_questions = [bookmark.code_question for bookmark in bookmarks]
        serializer = CodeQuestionListSerializer(code_questions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取代码题目统计信息
        """
        total_questions = CodeQuestion.objects.filter(is_public=True).count()
        total_submissions = CodeSubmission.objects.filter(user=request.user).count()
        accepted_submissions = CodeSubmission.objects.filter(
            user=request.user,
            status='accepted'
        ).count()

        # 按语言统计
        language_stats = CodeSubmission.objects.filter(
            user=request.user
        ).values('language').annotate(
            count=Count('id'),
            accepted=Count('id', filter=Q(status='accepted'))
        )

        # 按难度统计
        difficulty_stats = CodeQuestion.objects.filter(
            is_public=True
        ).values('question__difficulty').annotate(
            count=Count('id')
        )

        return Response({
            'total_questions': total_questions,
            'total_submissions': total_submissions,
            'accepted_submissions': accepted_submissions,
            'acceptance_rate': round(
                (accepted_submissions / total_submissions * 100) if total_submissions > 0 else 0, 2
            ),
            'language_stats': list(language_stats),
            'difficulty_stats': list(difficulty_stats)
        })


class TestCaseViewSet(viewsets.ModelViewSet):
    """
    测试用例视图集
    """
    serializer_class = TestCaseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = TestCase.objects.select_related('code_question', 'code_question__question')
        code_question_id = self.request.query_params.get('code_question')
        if code_question_id:
            queryset = queryset.filter(code_question_id=code_question_id)
        return queryset.order_by('order', 'id')

    def perform_create(self, serializer):
        serializer.save()


class CodeSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    代码提交记录视图集
    """
    serializer_class = CodeSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CodeSubmission.objects.filter(
            user=self.request.user
        ).select_related('user', 'code_question', 'code_question__question')

        # 过滤
        code_question_id = self.request.query_params.get('code_question')
        if code_question_id:
            queryset = queryset.filter(code_question_id=code_question_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        获取最近的提交记录
        """
        limit = int(request.query_params.get('limit', 10))
        submissions = self.get_queryset()[:limit]
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)
