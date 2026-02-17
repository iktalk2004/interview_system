"""
代码题目测试数据生成脚本

使用方法：
python manage.py generate_code_questions
"""

from django.core.management.base import BaseCommand
from questions.models import Question, Category
from code_questions.models import CodeQuestion, TestCase
from users.models import User
import json


class Command(BaseCommand):
    help = 'Generate test code questions and test cases'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting code questions generation...'))

        # 获取或创建分类
        category, _ = Category.objects.get_or_create(
            name='Algorithm',
            defaults={'parent': None}
        )

        # 获取管理员用户
        try:
            creator = User.objects.filter(is_superuser=True).first()
            if not creator:
                creator = User.objects.first()
        except:
            creator = None

        # 创建示例题目
        questions_data = [
            {
                'title': 'Two Sum',
                'explanation': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                'difficulty': 1,
                'language': 'python',
                'template_code': '''def solution(nums, target):
    """
    :type nums: List[int]
    :type target: int
    :rtype: List[int]
    """
    # Write your code here
    pass
''',
                'starter_code': '''def solution(nums, target):
    """
    :type nums: List[int]
    :type target: int
    :rtype: List[int]
    """
    # Write your code here
    pass
''',
                'function_signature': 'def solution(nums, target):',
                'time_limit': 1000,
                'memory_limit': 256,
                'test_cases': [
                    {
                        'input_data': json.dumps({'nums': [2, 7, 11, 15], 'target': 9}),
                        'expected_output': json.dumps([0, 1]),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 1
                    },
                    {
                        'input_data': json.dumps({'nums': [3, 2, 4], 'target': 6}),
                        'expected_output': json.dumps([1, 2]),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 2
                    },
                    {
                        'input_data': json.dumps({'nums': [3, 3], 'target': 6}),
                        'expected_output': json.dumps([0, 1]),
                        'is_sample': False,
                        'is_hidden': True,
                        'order': 3
                    }
                ]
            },
            {
                'title': 'Reverse String',
                'explanation': 'Write a function that reverses a string. The input string is given as an array of characters s. You must do this by modifying the input array in-place with O(1) extra memory.',
                'difficulty': 1,
                'language': 'python',
                'template_code': '''def solution(s):
    """
    :type s: List[str]
    :rtype: None
    """
    # Write your code here
    pass
''',
                'starter_code': '''def solution(s):
    """
    :type s: List[str]
    :rtype: None
    """
    # Write your code here
    pass
''',
                'function_signature': 'def solution(s):',
                'time_limit': 1000,
                'memory_limit': 256,
                'test_cases': [
                    {
                        'input_data': json.dumps({'s': ['h', 'e', 'l', 'l', 'o']}),
                        'expected_output': json.dumps(['o', 'l', 'l', 'e', 'h']),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 1
                    },
                    {
                        'input_data': json.dumps({'s': ['H', 'a', 'n', 'n', 'a', 'h']}),
                        'expected_output': json.dumps(['h', 'a', 'n', 'n', 'a', 'H']),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 2
                    },
                    {
                        'input_data': json.dumps({'s': ['a', 'b', 'c', 'd']}),
                        'expected_output': json.dumps(['d', 'c', 'b', 'a']),
                        'is_sample': False,
                        'is_hidden': True,
                        'order': 3
                    }
                ]
            },
            {
                'title': 'Valid Parentheses',
                'explanation': 'Given a string s containing just the characters \'(\', \')\', \'{\', \'}\', \'[\' and \']\', determine if the input string is valid.',
                'difficulty': 2,
                'language': 'python',
                'template_code': '''def solution(s):
    """
    :type s: str
    :rtype: bool
    """
    # Write your code here
    pass
''',
                'starter_code': '''def solution(s):
    """
    :type s: str
    :rtype: bool
    """
    # Write your code here
    pass
''',
                'function_signature': 'def solution(s):',
                'time_limit': 1000,
                'memory_limit': 256,
                'test_cases': [
                    {
                        'input_data': json.dumps({'s': '()'}),
                        'expected_output': json.dumps(True),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 1
                    },
                    {
                        'input_data': json.dumps({'s': '()[]{}'}),
                        'expected_output': json.dumps(True),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 2
                    },
                    {
                        'input_data': json.dumps({'s': '(]'}),
                        'expected_output': json.dumps(False),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 3
                    },
                    {
                        'input_data': json.dumps({'s': '([)]'}),
                        'expected_output': json.dumps(False),
                        'is_sample': False,
                        'is_hidden': True,
                        'order': 4
                    },
                    {
                        'input_data': json.dumps({'s': '{[]}'}),
                        'expected_output': json.dumps(True),
                        'is_sample': False,
                        'is_hidden': True,
                        'order': 5
                    }
                ]
            },
            {
                'title': 'Maximum Subarray',
                'explanation': 'Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.',
                'difficulty': 2,
                'language': 'python',
                'template_code': '''def solution(nums):
    """
    :type nums: List[int]
    :rtype: int
    """
    # Write your code here
    pass
''',
                'starter_code': '''def solution(nums):
    """
    :type nums: List[int]
    :rtype: int
    """
    # Write your code here
    pass
''',
                'function_signature': 'def solution(nums):',
                'time_limit': 1000,
                'memory_limit': 256,
                'test_cases': [
                    {
                        'input_data': json.dumps({'nums': [-2, 1, -3, 4, -1, 2, 1, -5, 4]}),
                        'expected_output': json.dumps(6),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 1
                    },
                    {
                        'input_data': json.dumps({'nums': [1]}),
                        'expected_output': json.dumps(1),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 2
                    },
                    {
                        'input_data': json.dumps({'nums': [5, 4, -1, 7, 8]}),
                        'expected_output': json.dumps(23),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 3
                    },
                    {
                        'input_data': json.dumps({'nums': [-1]}),
                        'expected_output': json.dumps(-1),
                        'is_sample': False,
                        'is_hidden': True,
                        'order': 4
                    }
                ]
            },
            {
                'title': 'Merge Two Sorted Lists',
                'explanation': 'Merge two sorted linked lists and return it as a sorted list. The list should be made by splicing together the nodes of the first two lists.',
                'difficulty': 2,
                'language': 'python',
                'template_code': '''def solution(list1, list2):
    """
    :type list1: List[int]
    :type list2: List[int]
    :rtype: List[int]
    """
    # Write your code here
    pass
''',
                'starter_code': '''def solution(list1, list2):
    """
    :type list1: List[int]
    :type list2: List[int]
    :rtype: List[int]
    """
    # Write your code here
    pass
''',
                'function_signature': 'def solution(list1, list2):',
                'time_limit': 1000,
                'memory_limit': 256,
                'test_cases': [
                    {
                        'input_data': json.dumps({'list1': [1, 2, 4], 'list2': [1, 3, 4]}),
                        'expected_output': json.dumps([1, 1, 2, 3, 4, 4]),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 1
                    },
                    {
                        'input_data': json.dumps({'list1': [], 'list2': []}),
                        'expected_output': json.dumps([]),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 2
                    },
                    {
                        'input_data': json.dumps({'list1': [], 'list2': [0]}),
                        'expected_output': json.dumps([0]),
                        'is_sample': True,
                        'is_hidden': False,
                        'order': 3
                    }
                ]
            }
        ]

        created_count = 0
        for q_data in questions_data:
            # 创建基础题目
            question = Question.objects.create(
                title=q_data['title'],
                explanation=q_data['explanation'],
                category=category,
                creator=creator,
                difficulty=q_data['difficulty'],
                is_approved=True
            )

            # 创建代码题目
            code_question = CodeQuestion.objects.create(
                question=question,
                language=q_data['language'],
                template_code=q_data['template_code'],
                starter_code=q_data['starter_code'],
                function_signature=q_data['function_signature'],
                time_limit=q_data['time_limit'],
                memory_limit=q_data['memory_limit'],
                is_public=True
            )

            # 创建测试用例
            for tc_data in q_data['test_cases']:
                TestCase.objects.create(
                    code_question=code_question,
                    input_data=tc_data['input_data'],
                    expected_output=tc_data['expected_output'],
                    is_sample=tc_data['is_sample'],
                    is_hidden=tc_data['is_hidden'],
                    order=tc_data['order']
                )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created question: {q_data["title"]}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} code questions!'
            )
        )
