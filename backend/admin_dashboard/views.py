from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, Q, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model

from users.models import User
from questions.models import Question, Category
from practice.models import Interaction
from analytics.models import UserStats, DailyStats

User = get_user_model()


class AdminDashboardViewSet(viewsets.GenericViewSet):
    """
    管理后台仪表板视图集
    """
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        获取数据概览统计
        """
        try:
            total_users = User.objects.count()
            total_questions = Question.objects.filter(is_approved=True).count()
            total_answers = Interaction.objects.filter(is_submitted=True, score__isnull=False).count()
            
            avg_score = 0
            if total_answers > 0:
                avg_score_result = Interaction.objects.filter(
                    is_submitted=True, 
                    score__isnull=False
                ).aggregate(avg=Avg('score'))
                avg_score = round(avg_score_result['avg'] or 0, 1)

            data = {
                'total_users': total_users,
                'total_questions': total_questions,
                'total_answers': total_answers,
                'avg_score': avg_score
            }

            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def trend_data(self, request):
        """
        获取答题趋势数据
        """
        try:
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)

            trend_data = Interaction.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
                is_submitted=True
            ).annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                count=Count('id'),
                avg_score=Avg('score')
            ).order_by('date')

            dates = []
            counts = []
            scores = []

            for item in trend_data:
                dates.append(item['date'].strftime('%Y-%m-%d'))
                counts.append(item['count'])
                scores.append(round(item['avg_score'] or 0, 1))

            data = {
                'dates': dates,
                'counts': counts,
                'scores': scores
            }

            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def category_distribution(self, request):
        """
        获取题目分布数据
        """
        try:
            categories = Category.objects.all()
            data = []

            for category in categories:
                question_count = Question.objects.filter(
                    category=category,
                    is_approved=True
                ).count()
                
                if question_count > 0:
                    data.append({
                        'name': category.name,
                        'value': question_count
                    })

            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """
        获取最近活动记录
        """
        try:
            limit = int(request.query_params.get('limit', 10))
            
            recent_interactions = Interaction.objects.select_related(
                'user', 'question'
            ).order_by('-created_at')[:limit]

            activities = []
            for interaction in recent_interactions:
                action = '提交答案' if interaction.is_submitted else '查看题目'
                target = interaction.question.title if interaction.question else '未知'
                user = interaction.user.username
                time = interaction.created_at.strftime('%Y-%m-%d %H:%M')

                activities.append({
                    'user': user,
                    'action': action,
                    'target': target,
                    'time': time
                })

            return Response(activities)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """
        获取用户活跃度数据
        """
        try:
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)

            active_users = User.objects.filter(
                interaction__created_at__date__gte=start_date
            ).annotate(
                date=TruncDate('interaction__created_at')
            ).values('date').annotate(
                count=Count('id', distinct=True)
            ).order_by('date')

            dates = []
            counts = []

            for item in active_users:
                dates.append(item['date'].strftime('%Y-%m-%d'))
                counts.append(item['count'])

            data = {
                'dates': dates,
                'counts': counts
            }

            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def user_list(self, request):
        """
        获取用户列表
        """
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            search = request.query_params.get('search', '')

            queryset = User.objects.all()

            if search:
                queryset = queryset.filter(
                    Q(username__icontains=search) | 
                    Q(email__icontains=search)
                )

            total = queryset.count()
            start = (page - 1) * page_size
            end = start + page_size
            users = queryset[start:end]

            users_data = []
            for user in users:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff
                })

            return Response({
                'results': users_data,
                'count': total,
                'page': page,
                'page_size': page_size
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def create_user(self, request):
        """
        创建用户
        """
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')

            if not username or not email or not password:
                return Response(
                    {'error': '用户名、邮箱和密码不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(username=username).exists():
                return Response(
                    {'error': '用户名已存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': '邮箱已被使用'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            return Response({
                'message': '用户创建成功',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['delete'], url_path='delete-user/(?P<user_id>\d+)')
    def delete_user(self, request, user_id=None):
        """
        删除用户
        """
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({'message': '用户删除成功'})
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def question_list(self, request):
        """
        获取题目列表
        """
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            search = request.query_params.get('search', '')
            category_id = request.query_params.get('category_id')
            difficulty = request.query_params.get('difficulty')

            queryset = Question.objects.select_related('category').all()

            if search:
                queryset = queryset.filter(title__icontains=search)

            if category_id:
                queryset = queryset.filter(category_id=category_id)

            if difficulty:
                queryset = queryset.filter(difficulty=difficulty)

            total = queryset.count()
            start = (page - 1) * page_size
            end = start + page_size
            questions = queryset[start:end]

            questions_data = []
            for question in questions:
                questions_data.append({
                    'id': question.id,
                    'title': question.title,
                    'difficulty': question.difficulty,
                    'category': {
                        'id': question.category.id if question.category else None,
                        'name': question.category.name if question.category else None
                    },
                    'is_approved': question.is_approved,
                    'created_at': question.created_at.isoformat() if question.created_at else None
                })

            return Response({
                'results': questions_data,
                'count': total,
                'page': page,
                'page_size': page_size
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['delete'], url_path='delete-question/(?P<question_id>\d+)')
    def delete_question(self, request, question_id=None):
        """
        删除题目
        """
        try:
            question = Question.objects.get(id=question_id)
            question.delete()
            return Response({'message': '题目删除成功'})
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

    @action(detail=False, methods=['get'])
    def category_list(self, request):
        """
        获取分类列表
        """
        try:
            categories = Category.objects.select_related('parent').all()
            
            categories_data = []
            for category in categories:
                categories_data.append({
                    'id': category.id,
                    'name': category.name,
                    'parent': {
                        'id': category.parent.id if category.parent else None,
                        'name': category.parent.name if category.parent else None
                    }
                })

            return Response(categories_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def create_category(self, request):
        """
        创建分类
        """
        try:
            name = request.data.get('name')
            parent_id = request.data.get('parent')

            if not name:
                return Response(
                    {'error': '分类名称不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            parent = None
            if parent_id:
                parent = Category.objects.get(id=parent_id)

            category = Category.objects.create(
                name=name,
                parent=parent
            )

            return Response({
                'message': '分类创建成功',
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'parent': {
                        'id': category.parent.id if category.parent else None,
                        'name': category.parent.name if category.parent else None
                    }
                }
            })
        except Category.DoesNotExist:
            return Response(
                {'error': '父分类不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['delete'], url_path='delete-category/(?P<category_id>\d+)')
    def delete_category(self, request, category_id=None):
        """
        删除分类
        """
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return Response({'message': '分类删除成功'})
        except Category.DoesNotExist:
            return Response(
                {'error': '分类不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def settings(self, request):
        """
        获取系统设置
        """
        try:
            from django.conf import settings

            data = {
                'systemName': getattr(settings, 'SYSTEM_NAME', '程序员八股文答题训练系统'),
                'systemDescription': getattr(settings, 'SYSTEM_DESCRIPTION', '基于协同过滤的智能答题训练平台'),
                'allowRegister': getattr(settings, 'ALLOW_REGISTER', True),
                'maintenanceMode': getattr(settings, 'MAINTENANCE_MODE', False)
            }

            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def update_settings(self, request):
        """
        更新系统设置
        """
        try:
            from django.conf import settings
            
            settings.SYSTEM_NAME = request.data.get('systemName', settings.SYSTEM_NAME)
            settings.SYSTEM_DESCRIPTION = request.data.get('systemDescription', settings.SYSTEM_DESCRIPTION)
            settings.ALLOW_REGISTER = request.data.get('allowRegister', settings.ALLOW_REGISTER)
            settings.MAINTENANCE_MODE = request.data.get('maintenanceMode', settings.MAINTENANCE_MODE)

            return Response({'message': '设置保存成功'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
