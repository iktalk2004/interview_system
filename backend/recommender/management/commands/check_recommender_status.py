from django.core.management.base import BaseCommand
from django.db import models
from practice.models import Interaction
from questions.models import Question
from users.models import User
from recommender.models import UserSimilarity, QuestionSimilarity


class Command(BaseCommand):
    help = '检查推荐系统数据状态'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== 推荐系统数据状态检查 ===\n'))

        users = User.objects.filter(interaction__isnull=False).distinct()
        questions = Question.objects.filter(interaction__isnull=False, is_approved=True).distinct()
        interactions = Interaction.objects.filter(is_submitted=True, score__isnull=False)

        self.stdout.write(f'📊 基础数据:')
        self.stdout.write(f'  用户数: {users.count()}')
        self.stdout.write(f'  题目数: {questions.count()}')
        self.stdout.write(f'  答题记录数: {interactions.count()}')

        score_stats = interactions.aggregate(
            min_score=models.Min('score'),
            max_score=models.Max('score'),
            avg_score=models.Avg('score')
        )

        self.stdout.write(f'\n📈 分数统计:')
        self.stdout.write(f'  最低分: {score_stats["min_score"] or 0:.1f}')
        self.stdout.write(f'  最高分: {score_stats["max_score"] or 0:.1f}')
        self.stdout.write(f'  平均分: {score_stats["avg_score"] or 0:.1f}')

        high_score_count = interactions.filter(score__gte=60).count()
        self.stdout.write(f'  高分记录(>=60): {high_score_count}')

        user_similarities = UserSimilarity.objects.all()
        question_similarities = QuestionSimilarity.objects.all()

        self.stdout.write(f'\n🔗 相似度矩阵:')
        self.stdout.write(f'  用户相似度记录: {user_similarities.count()}')

        if user_similarities.exists():
            high_sim = user_similarities.filter(similarity_score__gte=0.5).count()
            self.stdout.write(f'  高相似度(>=0.5): {high_sim}')

            top_sim = user_similarities.order_by('-similarity_score').first()
            if top_sim:
                self.stdout.write(f'  最高相似度: {top_sim.similarity_score:.3f}')
                self.stdout.write(f'  最高相似度对: {top_sim.user_a.username} <-> {top_sim.user_b.username}')

        self.stdout.write(f'  题目相似度记录: {question_similarities.count()}')

        if question_similarities.exists():
            high_sim = question_similarities.filter(similarity_score__gte=0.5).count()
            self.stdout.write(f'  高相似度(>=0.5): {high_sim}')

            top_sim = question_similarities.order_by('-similarity_score').first()
            if top_sim:
                self.stdout.write(f'  最高相似度: {top_sim.similarity_score:.3f}')

        self.stdout.write(f'\n👥 用户答题情况:')
        for user in users[:5]:
            user_interactions = interactions.filter(user=user)
            count = user_interactions.count()
            avg = user_interactions.aggregate(avg=models.Avg('score'))['avg'] or 0
            self.stdout.write(f'  {user.username}: {count}题, 平均{avg:.1f}分')

        if users.count() > 5:
            self.stdout.write(f'  ... (还有 {users.count() - 5} 个用户)')

        self.stdout.write(f'\n📝 题目答题情况:')
        for question in questions[:5]:
            q_interactions = interactions.filter(question=question)
            count = q_interactions.count()
            avg = q_interactions.aggregate(avg=models.Avg('score'))['avg'] or 0
            self.stdout.write(f'  Q{question.id} ({question.title[:20]}...): {count}人, 平均{avg:.1f}分')

        if questions.count() > 5:
            self.stdout.write(f'  ... (还有 {questions.count() - 5} 道题目)')

        self.stdout.write(f'\n✅ 推荐系统就绪状态:')
        if user_similarities.count() > 0 and question_similarities.count() > 0:
            self.stdout.write(self.style.SUCCESS('  ✓ 推荐系统已就绪！可以正常使用'))
        else:
            self.stdout.write(self.style.WARNING('  ✗ 推荐系统未就绪'))
            if user_similarities.count() == 0:
                self.stdout.write(self.style.WARNING('    - 用户相似度矩阵为空'))
            if question_similarities.count() == 0:
                self.stdout.write(self.style.WARNING('    - 题目相似度矩阵为空'))
            self.stdout.write(self.style.WARNING('  请运行: python manage.py update_similarity_matrix')
