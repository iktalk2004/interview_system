1、两个名字相同但路径不同的 User 模型同时存在

```cmd
ERRORS:
auth.User.groups: (fields.E304) Reverse accessor 'Group.user_set' for 'auth.User.groups' clashes with reverse accessor for 'users.User.groups'.
        HINT: Add or change a related_name argument to the definition for 'auth.User.groups' or 'users.User.groups'.
auth.User.user_permissions: (fields.E304) Reverse accessor 'Permission.user_set' for 'auth.User.user_permissions' clashes with reverse accessor for 'users.User.user_permissions'.
        HINT: Add or change a related_name argument to the definition for 'auth.User.user_permissions' or 'users.User.user_permissions'.
users.User.groups: (fields.E304) Reverse accessor 'Group.user_set' for 'users.User.groups' clashes with reverse accessor for 'auth.User.groups'.
        HINT: Add or change a related_name argument to the definition for 'users.User.groups' or 'auth.User.groups'.
users.User.user_permissions: (fields.E304) Reverse accessor 'Permission.user_set' for 'users.User.user_permissions' clashes with reverse accessor for 'auth.User.user_permissions'.
        HINT: Add or change a related_name argument to the definition for 'users.User.user_permissions' or 'auth.User.user_permissions'.
```

报错原因：

**auth.User** 和 **users.User** 同时存在，模型名称相同。而 **groups** 和 **user_permissions** 这两个字段都是 **ManyToManyField**，它们会自动为反向关系创建 **accessor**（反向查询的名称），默认都叫

```cmd
group.user_set          # Group → 所有属于这个组的用户
permission.user_set     # Permission → 拥有这个权限的所有用户
```

Django 系统检查（system check）在启动和 makemigrations 时发现这个冲突，就直接报错了。

解决方法：

<u>自定义的 **User** 模型里，显式指定 **related_name**，把反向查询名称改掉。</u>

```python
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    # 你的其他字段...

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',      # ← 必须改名！
        /related_name='%(app_label)s_%(class)s_set',   # 自动变成 users_user_set
        blank=True,
        help_text='The groups this user belongs to...',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',  # ← 也要改名！
        \related_name='%(app_label)s_%(class)s_permissions',  # 变成 users_user_permissions
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
```

