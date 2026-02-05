from django.core.management.base import BaseCommand
from practice.models import Interaction
from questions.models import Question
from users.models import User
from recommender.algorithms import CollaborativeFiltering
from recommender.models import UserSimilarity, QuestionSimilarity, Recommendation


class Command(BaseCommand):
    help = '一键修复推荐系统 - 重新生成数据、更新相似度矩阵、清理旧推荐'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=30,
            help='生成的用户数量'
        )
        parser.add_argument(
            '--interactions',
            type=int,
            default=300,
            help='生成的交互数量'
        )
        parser.add_argument(
            '--min-common',
            type=int,
            default=1,
            help='最小共同答题数'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_interactions = options['interactions']
        min_common = options['min_common']

        self.stdout.write(self.style.SUCCESS('=== 推荐系统一键修复 ===\n'))

        self.stdout.write('🔧 步骤 1/5: 清理旧数据...')
        try:
            UserSimilarity.objects.all().delete()
            QuestionSimilarity.objects.all().delete()
            Recommendation.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('  ✓ 旧数据清理完成'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ 清理失败: {str(e)}'))
            return

        self.stdout.write('\n📊 步骤 2/5: 检查基础数据...')
        users_count = User.objects.filter(interaction__isnull=False).distinct().count()
        questions_count = Question.objects.filter(is_approved=True).count()
        interactions_count = Interaction.objects.filter(is_submitted=True, score__isnull=False).count()

        self.stdout.write(f'  用户数: {users_count}')
        self.stdout.write(f'  题目数: {questions_count}')
        self.stdout.write(f'  答题记录数: {interactions_count}')

        if users_count < 2:
            self.stdout.write(self.style.WARNING('  ⚠ 用户数量不足，尝试生成测试数据...'))
            self.stdout.write(self.style.WARNING('  请手动运行: python manage.py generate_test_data --users 30 --interactions 300'))
            return

        if questions_count < 2:
            self.stdout.write(self.style.WARNING('  ⚠ 题目数量不足，请先生成题目'))
            self.stdout.write(self.style.WARNING('  请运行: python manage.py generate_test_questions --questions 50'))
            return

        if interactions_count < 10:
            self.stdout.write(self.style.WARNING('  ⚠ 答题记录过少，尝试生成测试数据...'))
            self.stdout.write(self.style.WARNING('  请手动运行: python manage.py generate_test_data --users 30 --interactions 300'))
            return

        self.stdout.write(self.style.SUCCESS('  ✓ 基础数据检查通过'))

        self.stdout.write('\n🔗 步骤 3/5: 更新用户相似度矩阵...')
        try:
            user_count = CollaborativeFiltering.update_user_similarities(
                min_common_questions=min_common
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ 用户相似度矩阵更新完成: {user_count} 条记录'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ 用户相似度矩阵更新失败: {str(e)}'))
            return

        self.stdout.write('\n🔗 步骤 4/5: 更新题目相似度矩阵...')
        try:
            question_count = CollaborativeFiltering.update_question_similarities(
                min_common_users=min_common
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ 题目相似度矩阵更新完成: {question_count} 条记录'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ 题目相似度矩阵更新失败: {str(e)}'))
            return

        self.stdout.write('\n✅ 步骤 5/5: 验证修复结果...')
        user_sim_count = UserSimilarity.objects.count()
        question_sim_count = QuestionSimilarity.objects.count()

        if user_sim_count > 0 and question_sim_count > 0:
            self.stdout.write(self.style.SUCCESS('\n🎉 推荐系统修复成功！'))
            self.stdout.write(f'  用户相似度记录: {user_sim_count}')
            self.stdout.write(f'  题目相似度记录: {question_sim_count}')
            self.stdout.write('\n📝 下一步操作:')
            self.stdout.write('  1. 登录系统')
            self.stdout.write('  2. 访问智能推荐页面')
            self.stdout.write('  3. 点击"刷新推荐"按钮')
            self.stdout.write('  4. 查看推荐结果')
        else:
            self.stdout.write(self.style.WARNING('\n⚠ 推荐系统可能仍有问题'))
            self.stdout.write(f'  用户相似度记录: {user_sim_count}')
            self.stdout.write(f'  题目相似度记录: {question_sim_count}')
            self.stdout.write('\n💡 建议:')
            self.stdout.write('  1. 生成更多测试数据')
            self.stdout.write('  2. 降低 --min-common 参数值')
            self.stdout.write('  3. 运行 python manage.py check_recommender_status 查看详情')
