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



2、Given token not valid for any token type，Login.vue:32   POST http://localhost:8000/api/users/login/ 401 (Unauthorized)。

报错原因：

token过期，前端没有设置token刷新机制，localStorage中可能存在无效token。

解决办法：

```js
// 在api.js中添加token刷新拦截器，处理token过期的问题

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// 响应拦截器：处理token过期
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        if (error.response.status === 401 && !originalRequest._retry) {
            if (!isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({resolve, reject});
                }).then(token => {
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return api(originalRequest);
                }).catch(err => {
                    return Promise.reject(err);
                })
            }
            originalRequest._retry = true;
            isRefreshing = true;

            const refresh_token = localStorage.getItem('refresh_token');

            if (!refresh_token) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return Promise.reject(error);
            }

            try {
                const response = await axios.post('http://localhost:8000/api/token/refresh/', {
                    refresh: refresh_token
                });

                const newAccessToken = response.data.access;
                localStorage.setItem('access_token', newAccessToken);

                originalRequest.headers.Authorization = 'Bearer ${newAccessToken}';

                processQueue(null, newAccessToken);

                return api(originalRequest);
            } catch (refreshError) {
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/login';
                processQueue(refreshError, null)
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
)
```

```python
# 同时后端添加处理tokenRefresh的ViewApi
from rest_framework_simplejwt.views import TokenRefreshView
path("api/token/refresh", TokenRefreshView.as_view(), name="token_refresh")

```

3、未登录用户访问profile页面，报错401 (Unauthorized)。

报错原因：未登录用户访问profile的request没有携带token。

解决办法：在**前端路由设置**中添加**路由守卫**保护需要登陆的页面，同时在fetchprofile**优化401error的处理**。

```js
{path: '/profile', component: Profile, meta: {requiresAuth: true}}

// 全局前置守卫
router.beforeEach((to, from, next) => {
    const isAuthenticated = !!localStorage.getItem('access_token');

    if (to.meta.requiresAuth && !isAuthenticated) {
        // 跳转到登录页面, 并带上当前页面的路径，以便登录后返回
        next({
            path: '/login',
            query: {redirect: to.fullPath}
        });
    } else {
        // 如果已登录有token，正常放行
        next();
    }
});
```

