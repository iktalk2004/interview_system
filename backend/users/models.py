from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    preferences = models.JSONField(default=dict, blank=True)  # 用户偏好标签

    groups = models.ManyToManyField(
        #  必须重构反向查询名，否则会报错
        Group,
        related_name="%(app_label)s_%(class)s_set",  # 模型名_模型名_set
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",  # 用户所属的组
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        #  必须重构反向查询名，否则会报错
        Permission,
        related_name="%(app_label)s_%(class)s_set",  # 模型名_模型名_set
        blank=True,
        help_text="Specific permissions for this user.",  # 用户的权限
        verbose_name="user permissions",
    )