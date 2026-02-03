from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Sum, Max, Min
from .models import Interaction
from analytics.models import UserStats, DailyStats


@receiver(post_save, sender=Interaction)
def update_user_stats_on_interaction_save(sender, instance, created, **kwargs):
    """
    当交互记录保存时，更新用户统计数据
    """
    user = instance.user

    try:
        # 获取用户所有答题记录
        interactions = Interaction.objects.filter(user=user)
        answered = interactions.filter(score__isnull=False)

        # 计算统计数据
        total_answered = answered.count()
        total_viewed = interactions.filter(status='viewed').count()

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
        UserStats.objects.update_or_create(
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
    except Exception as e:
        print(f"Error updating user stats: {e}")


@receiver(post_save, sender=Interaction)
def update_daily_stats_on_interaction_save(sender, instance, created, **kwargs):
    """
    当交互记录保存时，更新每日统计数据
    """
    user = instance.user
    interaction_date = instance.created_at.date()

    try:
        # 获取当天的答题记录
        interactions = Interaction.objects.filter(
            user=user,
            created_at__date=interaction_date
        )

        answered = interactions.filter(score__isnull=False)

        questions_answered = answered.count()
        questions_viewed = interactions.filter(status='viewed').count()

        if questions_answered > 0:
            avg_score = answered.aggregate(avg=Avg('score'))['avg'] or 0
            time_spent = answered.aggregate(total=Sum('time_spent'))['total'] or 0
        else:
            avg_score = 0
            time_spent = 0

        # 更新或创建每日统计
        DailyStats.objects.update_or_create(
            user=user,
            date=interaction_date,
            defaults={
                'questions_answered': questions_answered,
                'questions_viewed': questions_viewed,
                'average_score': avg_score,
                'time_spent': time_spent
            }
        )
    except Exception as e:
        print(f"Error updating daily stats: {e}")
