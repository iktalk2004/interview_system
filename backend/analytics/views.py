from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Sum, Max, Min, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, date
from .models import UserStats, CategoryStats, DailyStats, PerformanceTrend
from .serializers import (
    UserStatsSerializer,
    CategoryStatsSerializer,
    DailyStatsSerializer,
    PerformanceTrendSerializer
)
from practice.models import Interaction
from questions.models import Question, Category
from users.models import User


class UserStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户统计视图集
    """
    queryset = UserStats.objects.all()
    serializer_class = UserStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 只返回当前用户的统计
        queryset = queryset.filter(user=user)

        return queryset

    @action(detail=False, methods=['post'])
    def update_stats(self, request):
        """
        更新用户统计数据
        """
        user = request.user

        try:
            # 获取用户答题记录
            interactions = Interaction.objects.filter(user=user)

            # 计算统计数据
            answered = interactions.filter(is_submitted=True, score__isnull=False)
            viewed = interactions.filter(status='viewed')

            total_answered = answered.count()
            total_viewed = viewed.count()

            if total_answered > 0:
                avg_score = answered.aggregate(avg=Avg('score'))['avg'] or 0
                highest_score = answered.aggregate(max=Max('score'))['max'] or 0
                lowest_score = answered.aggregate(min=Min('score'))['min'] or 0
                total_time = answered.aggregate(total=Sum('time_spent'))['total'] or 0
                avg_time = total_time / total_answered
            else:
                avg_score = 0
                highest_score = 0
                lowest_score = 0
                total_time = 0
                avg_time = 0

            favorite_count = interactions.filter(is_favorite=True).count()

            # 更新或创建用户统计
            stats, created = UserStats.objects.update_or_create(
                user=user,
                defaults={
                    'total_questions_answered': total_answered,
                    'total_questions_viewed': total_viewed,
                    'average_score': avg_score,
                    'highest_score': highest_score,
                    'lowest_score': lowest_score,
                    'total_time_spent': total_time,
                    'average_time_per_question': avg_time,
                    'favorite_count': favorite_count
                }
            )

            serializer = self.get_serializer(stats)
            return Response({
                'message': '用户统计更新成功',
                'stats': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    分类统计视图集
    """
    queryset = CategoryStats.objects.all()
    serializer_class = CategoryStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    @action(detail=False, methods=['post'])
    def update_stats(self, request):
        """
        更新分类统计数据
        """
        try:
            categories = Category.objects.all()

            for category in categories:
                # 获取该分类的题目
                questions = Question.objects.filter(category=category, is_approved=True)
                total_questions = questions.count()

                # 获取该分类的答题记录
                interactions = Interaction.objects.filter(
                    question__category=category,
                    score__isnull=False,
                    is_submitted=True
                )

                total_answers = interactions.count()

                if total_answers > 0:
                    avg_score = interactions.aggregate(avg=Avg('score'))['avg'] or 0

                    # 找出最难和最简单的题目
                    question_scores = interactions.values('question_id').annotate(
                        avg_score=Avg('score')
                    ).order_by('avg_score')

                    if question_scores.exists():
                        easiest_id = question_scores.first()['question_id']
                        most_difficult_id = question_scores.last()['question_id']

                        easiest = Question.objects.filter(id=easiest_id).first()
                        most_difficult = Question.objects.filter(id=most_difficult_id).first()
                    else:
                        easiest = None
                        most_difficult = None
                else:
                    avg_score = 0
                    easiest = None
                    most_difficult = None

                # 更新或创建分类统计
                CategoryStats.objects.update_or_create(
                    category=category,
                    defaults={
                        'total_questions': total_questions,
                        'total_answers': total_answers,
                        'average_score': avg_score,
                        'most_difficult': most_difficult,
                        'easiest': easiest
                    }
                )

            return Response({
                'message': '分类统计更新成功',
                'updated_count': categories.count()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DailyStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    每日统计视图集
    """
    queryset = DailyStats.objects.all()
    serializer_class = DailyStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 只返回当前用户的统计
        queryset = queryset.filter(user=user)

        # 日期过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # 按日期降序排序
        queryset = queryset.order_by('-date')

        return queryset

    @action(detail=False, methods=['post'])
    def update_stats(self, request):
        """
        更新每日统计数据
        """
        user = request.user
        target_date = request.data.get('date')

        try:
            if target_date:
                target_date = timezone.datetime.strptime(target_date, '%Y-%m-%d').date()
            else:
                target_date = timezone.now().date()

            # 获取当天的答题记录
            interactions = Interaction.objects.filter(
                user=user,
                created_at__date=target_date
            )

            answered = interactions.filter(is_submitted=True, score__isnull=False)
            viewed = interactions.filter(status='viewed')

            questions_answered = answered.count()
            questions_viewed = viewed.count()

            if questions_answered > 0:
                avg_score = answered.aggregate(avg=Avg('score'))['avg'] or 0
                time_spent = answered.aggregate(total=Sum('time_spent'))['total'] or 0
            else:
                avg_score = 0
                time_spent = 0

            # 更新或创建每日统计
            daily_stats, created = DailyStats.objects.update_or_create(
                user=user,
                date=target_date,
                defaults={
                    'questions_answered': questions_answered,
                    'questions_viewed': questions_viewed,
                    'average_score': avg_score,
                    'time_spent': time_spent
                }
            )

            serializer = self.get_serializer(daily_stats)
            return Response({
                'message': '每日统计更新成功',
                'stats': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PerformanceTrendViewSet(viewsets.ReadOnlyModelViewSet):
    """
    性能趋势视图集
    """
    queryset = PerformanceTrend.objects.all()
    serializer_class = PerformanceTrendSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # 只返回当前用户的趋势
        queryset = queryset.filter(user=user)

        # 日期过滤
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # 按日期降序排序
        queryset = queryset.order_by('-date')

        return queryset

    @action(detail=False, methods=['post'])
    def calculate_trends(self, request):
        """
        计算性能趋势
        """
        user = request.user
        days = int(request.data.get('days', 30))

        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)

            # 获取每日统计
            daily_stats = DailyStats.objects.filter(
                user=user,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')

            # 计算趋势
            stats_list = list(daily_stats)
            trends = []

            for i in range(1, len(stats_list)):
                prev_stat = stats_list[i - 1]
                curr_stat = stats_list[i]

                # 分数趋势
                if prev_stat.average_score > 0:
                    score_trend = curr_stat.average_score - prev_stat.average_score
                else:
                    score_trend = 0

                # 准确率趋势（用平均分代表）
                accuracy_trend = score_trend

                # 速度趋势（平均用时变化）
                if prev_stat.questions_answered > 0 and curr_stat.questions_answered > 0:
                    prev_avg_time = prev_stat.time_spent / prev_stat.questions_answered
                    curr_avg_time = curr_stat.time_spent / curr_stat.questions_answered
                    speed_trend = prev_avg_time - curr_avg_time  # 正值表示速度提升
                else:
                    speed_trend = 0

                # 保存趋势
                PerformanceTrend.objects.update_or_create(
                    user=user,
                    date=curr_stat.date,
                    defaults={
                        'score_trend': score_trend,
                        'accuracy_trend': accuracy_trend,
                        'speed_trend': speed_trend
                    }
                )

                trends.append({
                    'date': curr_stat.date,
                    'score_trend': score_trend,
                    'accuracy_trend': accuracy_trend,
                    'speed_trend': speed_trend
                })

            return Response({
                'message': '性能趋势计算成功',
                'trends': trends,
                'count': len(trends)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnalyticsDashboardViewSet(viewsets.GenericViewSet):
    """
    分析仪表板视图集
    提供综合分析数据
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        获取用户概览数据
        """
        user = request.user

        try:
            # 获取用户统计
            user_stats, _ = UserStats.objects.get_or_create(user=user)

            # 获取最近7天的每日统计
            seven_days_ago = timezone.now().date() - timedelta(days=7)
            recent_daily_stats = DailyStats.objects.filter(
                user=user,
                date__gte=seven_days_ago
            ).order_by('-date')

            # 获取最近的性能趋势
            recent_trends = PerformanceTrend.objects.filter(
                user=user
            ).order_by('-date')[:7]

            # 计算本周数据
            week_start = timezone.now().date() - timedelta(days=timezone.now().weekday())
            week_stats = DailyStats.objects.filter(
                user=user,
                date__gte=week_start
            ).aggregate(
                total_answered=Sum('questions_answered'),
                total_viewed=Sum('questions_viewed'),
                avg_score=Avg('average_score')
            )

            data = {
                'user_stats': UserStatsSerializer(user_stats).data,
                'recent_daily_stats': DailyStatsSerializer(recent_daily_stats, many=True).data,
                'recent_trends': PerformanceTrendSerializer(recent_trends, many=True).data,
                'week_stats': {
                    'total_answered': week_stats['total_answered'] or 0,
                    'total_viewed': week_stats['total_viewed'] or 0,
                    'avg_score': week_stats['avg_score'] or 0
                }
            }

            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """
        获取排行榜数据
        """
        try:
            # 按平均分排名
            top_by_score = UserStats.objects.filter(
                total_questions_answered__gte=10  # 至少答题10道
            ).order_by('-average_score')[:10]

            # 按答题数排名
            top_by_count = UserStats.objects.filter(
                total_questions_answered__gte=10
            ).order_by('-total_questions_answered')[:10]

            data = {
                'top_by_score': UserStatsSerializer(top_by_score, many=True).data,
                'top_by_count': UserStatsSerializer(top_by_count, many=True).data
            }

            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
