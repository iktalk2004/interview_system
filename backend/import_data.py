import os
import sys
import django
from django.conf import settings
import pandas as pd

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 正确设置 Django 配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 确保在导入模型前完成 Django 初始化
django.setup()

# 现在可以安全导入模型
from questions.models import Category, Question
from users.models import User


def get_difficulty_value(difficulty_str):
    """将中文难度转换为数字"""
    difficulty_map = {
        '易': 1,
        '简单': 1,
        '容易': 1,
        '中': 2,
        '中等': 2,
        '一般': 2,
        '难': 3,
        '困难': 3,
        '较难': 3,
    }
    # 转换为小写并去除空白字符，增加匹配准确性
    normalized = str(difficulty_str).strip().lower()
    for key, value in difficulty_map.items():
        if key.lower() in normalized or normalized in key.lower():
            return value
    # 如果没找到匹配项，返回默认值1（易）
    print(f"警告: 未识别的难度级别 '{difficulty_str}'，默认设为 1")
    return 1


# 获取或创建一个默认用户作为创建者
try:
    # 尝试获取admin用户，如果没有则获取第一个用户
    default_creator = User.objects.get(username='admin')
except User.DoesNotExist:
    # 如果没有admin用户，则尝试获取任意一个用户
    first_user = User.objects.first()
    if first_user:
        default_creator = first_user
    else:
        # 如果没有任何用户，创建一个默认用户
        default_creator = User.objects.create_user(
            username='system_admin',
            email='admin@example.com',
            password='default_password'
        )
        print(f"创建了默认用户: {default_creator.username}")

df = pd.read_excel('..\面试题目.xlsx')
for _, row in df.iterrows():
    category, _ = Category.objects.get_or_create(name=row['category'])
    Question.objects.create(
        title=row['title'],
        answer=row['answer'],
        category=category,
        difficult=get_difficulty_value(row['difficulty']),  # 使用转换函数
        is_approved=True,
        explanation=row['explanation'],
        creator=default_creator,  # 使用实际的 User 对象
    )
