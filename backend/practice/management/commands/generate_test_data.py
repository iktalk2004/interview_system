from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Avg
from users.models import User
from questions.models import Question, Category
from practice.models import Interaction
from faker import Faker
import random
from datetime import timedelta


class Command(BaseCommand):
    help = '生成模拟用户和交互数据用于测试推荐系统和数据分析'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='生成的用户数量'
        )
        parser.add_argument(
            '--interactions',
            type=int,
            default=500,
            help='生成的交互数量'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_interactions = options['interactions']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('清除现有数据...'))
            Interaction.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('数据清除完成'))

        fake = Faker('zh_CN')

        self.stdout.write(f'开始生成 {num_users} 个用户和 {num_interactions} 条交互记录...')

        questions = list(Question.objects.filter(is_approved=True))
        if not questions:
            self.stdout.write(self.style.ERROR('没有找到已审核的题目，请先创建题目'))
            return

        categories = list(Category.objects.all())

        tech_preferences = [
            'Python', 'Java', 'JavaScript', 'Vue', 'React',
            'Django', 'Flask', 'Spring Boot', 'Node.js',
            'MySQL', 'PostgreSQL', 'MongoDB',
            '算法与数据结构', '排序算法', '树结构', '图论'
        ]

        users = []
        for i in range(num_users):
            username = fake.user_name()
            email = fake.email()
            
            while User.objects.filter(username=username).exists():
                username = fake.user_name()
            
            while User.objects.filter(email=email).exists():
                email = fake.email()

            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                bio=fake.text(max_nb_chars=100),
                is_staff=random.random() < 0.1,
                is_active=True
            )

            user.preferences = self.generate_preferences(fake, tech_preferences)
            user.save()

            users.append(user)
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'已生成 {i + 1}/{num_users} 个用户')

        self.stdout.write(self.style.SUCCESS(f'用户生成完成: {num_users} 个'))

        interactions = []
        for i in range(num_interactions):
            user = random.choice(users)
            question = random.choice(questions)

            existing_interaction = Interaction.objects.filter(
                user=user,
                question=question,
                is_submitted=True
            ).first()

            if existing_interaction:
                continue

            is_submitted = random.random() < 0.7
            is_favorite = random.random() < 0.2
            
            time_spent = random.randint(30, 1800)
            
            score = None
            if is_submitted:
                base_score = random.uniform(50, 100)
                difficulty_factor = (4 - question.difficulty) * 5
                score = min(100, max(0, base_score + difficulty_factor))
                score = round(score, 1)

            interaction = Interaction.objects.create(
                user=user,
                question=question,
                answer=self.generate_answer(fake, question.title),
                score=score,
                time_spent=time_spent,
                is_submitted=is_submitted,
                is_favorite=is_favorite,
                status='submitted' if is_submitted else 'viewed'
            )

            interactions.append(interaction)
            
            if (i + 1) % 50 == 0:
                self.stdout.write(f'已生成 {i + 1}/{num_interactions} 条交互记录')

        self.stdout.write(self.style.SUCCESS(f'交互记录生成完成: {len(interactions)} 条'))

        self.generate_statistics()

    def generate_preferences(self, fake, tech_preferences):
        num_prefs = random.randint(1, 5)
        selected_prefs = random.sample(tech_preferences, num_prefs)
        
        preferences = {}
        for pref in selected_prefs:
            if pref in ['Python', 'Java', 'JavaScript']:
                sub_prefs = random.sample([
                    f'{pref}基础', f'{pref}进阶', f'{pref}专题'
                ], random.randint(1, 2))
                preferences[pref] = sub_prefs
            else:
                preferences[pref] = [pref]
        
        return preferences

    def generate_answer(self, fake, question_title):
        answer_templates = [
            f'{question_title}是一个很重要的概念，在实际开发中经常使用。',
            f'关于{question_title}，我认为主要包含以下几个方面...',
            f'{question_title}的核心思想是...',
            f'在处理{question_title}时，需要注意...',
            f'{fake.sentence()} {fake.sentence()} {fake.sentence()}',
        ]
        
        answer_length = random.randint(50, 300)
        answer = fake.text(max_nb_chars=answer_length)
        
        return answer

    def generate_statistics(self):
        total_users = User.objects.count()
        total_interactions = Interaction.objects.count()
        submitted_interactions = Interaction.objects.filter(is_submitted=True).count()
        favorite_interactions = Interaction.objects.filter(is_favorite=True).count()
        
        avg_score = 0
        if submitted_interactions > 0:
            avg_score_result = Interaction.objects.filter(
                is_submitted=True,
                score__isnull=False
            ).aggregate(avg=models.Avg('score'))
            avg_score = avg_score_result['avg'] or 0

        self.stdout.write(self.style.SUCCESS('\n数据统计:'))
        self.stdout.write(f'  总用户数: {total_users}')
        self.stdout.write(f'  总交互数: {total_interactions}')
        self.stdout.write(f'  已提交答题: {submitted_interactions}')
        self.stdout.write(f'  收藏数: {favorite_interactions}')
        self.stdout.write(f'  平均分数: {avg_score:.2f}')
