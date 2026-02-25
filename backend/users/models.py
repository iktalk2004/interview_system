from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


def user_avatar_upload_path(instance, filename):
    """
    生成用户头像上传路径
    """
    return f'avatars/user_{instance.id}/{filename}'


class User(AbstractUser):
    preferences = models.JSONField(default=dict, blank=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to=user_avatar_upload_path,
        blank=True,
        null=True,
        default='avatars/default/default-avatar.png',
        help_text='用户头像'
    )

    groups = models.ManyToManyField(
        Group,
        related_name="%(app_label)s_%(class)s_set",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="%(app_label)s_%(class)s_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username

    def get_avatar_url(self):
        """
        获取头像 URL
        """
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/media/avatars/default/default-avatar.png'
