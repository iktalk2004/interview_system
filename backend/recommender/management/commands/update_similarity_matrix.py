from django.core.management.base import BaseCommand
from practice.models import Interaction
from questions.models import Question
from users.models import User
from recommender.algorithms import CollaborativeFiltering
from recommender.models import UserSimilarity, QuestionSimilarity


class Command(BaseCommand):
    help = '更新推荐系统的相似度矩阵'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            choices=['all', 'user', 'question'],
            help='更新类型：all-全部, user-用户相似度, question-题目相似度'
        )
        parser.add_argument(
            '--min-common',
            type=int,
            default=2,
            help='最小共同答题数/用户数'
        )

    def handle(self, *args, **options):
        update_type = options['type']
        min_common = options['min_common']

        self.stdout.write(self.style.SUCCESS('开始更新推荐系统相似度矩阵...'))

        stats = {
            'users': User.objects.filter(interaction__isnull=False).distinct().count(),
            'questions': Question.objects.filter(interaction__isnull=False, is_approved=True).distinct().count(),
            'interactions': Interaction.objects.filter(is_submitted=True, score__isnull=False).count(),
            'user_similarities': UserSimilarity.objects.count(),
            'question_similarities': QuestionSimilarity.objects.count(),
        }

        self.stdout.write(f'当前数据统计:')
        self.stdout.write(f'  有答题记录的用户: {stats["users"]}')
        self.stdout.write(f'  有答题记录的题目: {stats["questions"]}')
        self.stdout.write(f'  已提交的答题记录: {stats["interactions"]}')
        self.stdout.write(f'  用户相似度记录: {stats["user_similarities"]}')
        self.stdout.write(f'  题目相似度记录: {stats["question_similarities"]}')

        if stats['users'] < 2:
            self.stdout.write(self.style.WARNING('用户数量不足，无法计算用户相似度'))
            return

        if stats['questions'] < 2:
            self.stdout.write(self.style.WARNING('题目数量不足，无法计算题目相似度'))
            return

        if stats['interactions'] < 10:
            self.stdout.write(self.style.WARNING('答题记录过少，相似度计算可能不准确'))

        if update_type in ['all', 'user']:
            self.stdout.write('\n正在更新用户相似度矩阵...')
            try:
                user_count = CollaborativeFiltering.update_user_similarities(
                    min_common_questions=min_common
                )
                self.stdout.write(self.style.SUCCESS(f'✓ 用户相似度矩阵更新完成: {user_count} 条记录'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ 用户相似度矩阵更新失败: {str(e)}'))

        if update_type in ['all', 'question']:
            self.stdout.write('\n正在更新题目相似度矩阵...')
            try:
                question_count = CollaborativeFiltering.update_question_similarities(
                    min_common_users=min_common
                )
                self.stdout.write(self.style.SUCCESS(f'✓ 题目相似度矩阵更新完成: {question_count} 条记录'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ 题目相似度矩阵更新失败: {str(e)}'))

        new_stats = {
            'user_similarities': UserSimilarity.objects.count(),
            'question_similarities': QuestionSimilarity.objects.count(),
        }

        self.stdout.write(self.style.SUCCESS('\n更新完成!'))
        self.stdout.write(f'  用户相似度记录: {stats["user_similarities"]} → {new_stats["user_similarities"]}')
        self.stdout.write(f'  题目相似度记录: {stats["question_similarities"]} → {new_stats["question_similarities"]}')

        if new_stats['user_similarities'] > 0:
            self.stdout.write(self.style.SUCCESS('\n现在可以使用推荐系统了!'))
            self.stdout.write('  前端访问智能推荐页面即可看到推荐结果')
        else:
            self.stdout.write(self.style.WARNING('\n相似度矩阵为空，可能原因:'))
            self.stdout.write('  1. 用户之间共同答题数太少')
            self.stdout.write('  2. 可以尝试降低 --min-common 参数值')
            self.stdout.write('  3. 生成更多测试数据')
