from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import User

User = get_user_model()


class UserModelTestCase(TestCase):
    """
    用户模型测试用例
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        """
        测试用户创建
        """
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_str_representation(self):
        """
        测试用户字符串表示
        """
        self.assertEqual(str(self.user), 'testuser')

    def test_user_preferences_field(self):
        """
        测试用户偏好字段
        """
        self.user.preferences = {'theme': 'dark', 'language': 'zh'}
        self.user.save()
        
        self.assertEqual(self.user.preferences['theme'], 'dark')
        self.assertEqual(self.user.preferences['language'], 'zh')

    def test_user_bio_field(self):
        """
        测试用户简介字段
        """
        self.user.bio = '这是一个测试用户'
        self.user.save()
        
        self.assertEqual(self.user.bio, '这是一个测试用户')
