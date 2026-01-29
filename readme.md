Anaconda隔离环境，激活环境。（pycharm自动加载conda环境）

```cmd
# 创建隔离环境
conda create -n Django python=3.14
# 激活环境
conda activate Django
```



# Django、Vue环境搭建

## 1、搭建后端环境

```cmd
# 创建django项目目录
cd E:\04_Interview_system\backend
django-admin startproject core .

# 创建app
python manage.py startapp users  # 用户管理
python manage.py startapp questions  # 题目库管理
python manage.py startapp practice  # 答题练习
python manage.py startapp recommender  # 推荐引擎
python manage.py startapp analytics  # 数据分析（可选）
```



```cmd
# 配置\core\settings.py
# 添加应用
INSTALLED_APPS = [
...
	'rest_framework',
    'corsheaders',
    'users',
    'questions',
    'practice',
    'recommender',
    'analytics',
]

# 添加跨域中间件
MIDDLEWARE = [
...
    'corsheaders.middleware.CorsMiddleware',
]

# 配置CORS，允许前端访问
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# 配置数据库（后期MYSQL替换如下）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```



```cmd
# 运行迁移，启动服务器

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```





## 2、设置Vue3项目

```cmd
# 创建前端项目框架
npm create vue@latest
npm create vite@latest

# 安装依赖
cd frontend
npm install
npm install axios  # API请求
npm install element-plus  # UI组件

# 配置axios（src\main.js）！！！
import axios from 'axios';
axios.defaults.baseURL = 'http://localhost:8000/api/';  # Django API基址

# 启动(默认端口5173)
npm run dev
```



安装依赖时可能比较慢，可以改用**国内镜像**

```cmd
# 查看当前源
npm config get registry
# 改成国内镜像源
npm config set registry https://registry.npmmirror.com
```



# 用户管理模块

权限控制使用django内置权限系统，实现用户\管理员区分。

## 注册

### 创建用户模型

```python
# 扩展Django的AbstractUser以添加偏好数据
# 方便地自定义 User 模型，同时仍然保留 Django 内置认证系统的大部分功能。
from django.contrib.auth.models import AbstractUser
```

**AbstractUser**内置字段（在此基础上添加**偏好标签字段**）

| 字段名           | 类型                            | 是否必填 | 默认值         | 说明                                           |
| ---------------- | ------------------------------- | -------- | -------------- | ---------------------------------------------- |
| id               | AutoField                       | -        | 自增           | 主键                                           |
| password         | CharField                       | 是       | (加密后的密码) | 存储加密后的密码                               |
| last_login       | DateTimeField                   | 否       | NULL           | 上次登录时间                                   |
| is_superuser     | BooleanField                    | 是       | False          | 是否超级用户（拥有所有权限）                   |
| username         | CharField                       | 是       | -              | 用户名（唯一）长度 max_length=150              |
| first_name       | CharField                       | 是       | ''             | 名，长度 max_length=150                        |
| last_name        | CharField                       | 是       | ''             | 姓，长度 max_length=150                        |
| email            | EmailField                      | 是       | ''             | 邮箱，默认非唯一（很多项目会改成 unique=True） |
| is_staff         | BooleanField                    | 是       | False          | 是否可以登录后台管理（admin 站点）             |
| is_active        | BooleanField                    | 是       | True           | 账户是否激活（可用于软删除/封禁账户）          |
| date_joined      | DateTimeField                   | 是       | now            | 注册/创建时间                                  |
| groups           | ManyToManyField (to Group)      | -        | -              | 用户所属权限组（多对多）                       |
| user_permissions | ManyToManyField (to Permission) | -        | -              | 用户额外获得的单个权限（多对多，不通过组）     |

创建完模型之后一定要记得迁移！！！（包括模型有任何的改变都需要重新迁移）

```cmd
python manage.py makemigrations users
python manage.py migrate
```



### 配置认证

```python
# core/settings.py
# 决定了你的 API 端点如何处理用户认证和权限检查。
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # DRF 会按顺序尝试这些认证类，直到成功认证或全部失败。
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # 用于admin
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # 默认所有接口都要登录，然后在具体视图上用 @permission_classes 放开某些公开接口（如注册、登录、获取验证码等）。
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### 创建序列化器

序列化器（Serializer） 是 Django REST Framework（DRF）中最核心、最重要的组件之一。

<u>把复杂的 Python 对象（如模型实例、列表、字典等）转换成可以在网络上传输的简单数据格式（通常是 JSON），以及反过来把接收到的 JSON 数据转换成 Python 对象。</u>

### 创建视图

权限控制：ProfileView **只允许认证用户**修改自己信息。管理员**可扩展为**ListView with IsAdminUser permission。

```python
# backend/users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # JWT 无需服务器端注销，客户端删除token即可。这里简单返回成功
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
```

### 配置URL

```python
# backend/users/urls.py
from django.urls import path
from .views import RegisterView, LoginView, ProfileView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]

# core/urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('api/users/', include('users.urls')),
]
```

### 配置axios（此处出现bug，详见bug2）

```js
// forntend/src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/users/',
  headers: { 'Content-Type': 'application/json' }
});

// 拦截器：添加token(很关键，没有这个后端无法收到token验证，即会报权限错误)！！！
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 还需一个响应拦截器处理token过期

export default api;
```

### 创建组件配置路由

```js
import {createRouter, createWebHistory} from 'vue-router'
import Register from '@/components/Register.vue';
import Login from '@/components/Login.vue';
import Profile from '@/components/Profile.vue';

const routes = [
    {path: '/', redirect: '/login'},
    {path: '/register', component: Register},
    {path: '/login', component: Login},
    {path: '/profile', component: Profile},
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;

```





**<u>！！！记住完成后需要在前端根目录的App.vue组件中集成路由！！！</u>**



**添加token拦截器以及刷新token拦截器**

```js
// 拦截器：添加token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token');  // access_token是Django返回的
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// 响应拦截器：处理token过期
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        if (error.response.status === 401) {
            if (!originalRequest._retry) {
                originalRequest._retry = true;  // 防止重复刷新,无限循环

                if (isRefreshing) {
                    // 如果正在刷新token，等待刷新完成
                    return new Promise((resolve, reject) => {
                        failedQueue.push({resolve, reject});
                    }).then(token => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return api(originalRequest);
                    }).catch(err => {
                        // 等待过程中发生错误，清理token并跳转
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('refresh_token');
                        window.location.href = '/login';
                        return Promise.reject(err);
                    })
                }

                // 状态修改为刷新中
                isRefreshing = true;

                const refresh_token = localStorage.getItem('refresh_token');

                if (!refresh_token) {
                    // 没有refresh_token，直接踢登录
                    localStorage.removeItem('access_token');
                    window.location.href = '/login';
                    return Promise.reject(error);
                }

                try {
                    const response = await axios.post(
                        'http://localhost:8000/api/token/refresh/', {
                            refresh: refresh_token
                        });

                    const newAccessToken = response.data.access;
                    localStorage.setItem('access_token', newAccessToken);

                    processQueue(null, newAccessToken);  // 更新队列中的所有请求

                    originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;  // 重新发送请求，使用新的token

                    return api(originalRequest);
                } catch (refreshError) {
                    // 刷新失败，清除token，大概率是refresh_token也过期了
                    processQueue(refreshError, null)
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('refresh_token')

                    // 提示用户并跳转
                    if (typeof window !== 'undefined' && typeof alert !== 'undefined') {
                        alert('登录已过期，请重新登录');
                    }

                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                } finally {
                    isRefreshing = false;
                }
            }
        }

        return Promise.reject(error);
    }
)
```



## 用户信息

### 二级标签处理

**Python** (一级)

- Python基础 (二级)
- Python进阶 (二级)
- Flask专题 (二级)
- Django专题 (二级)

存储为简单的JSON {tags: ['Python', 'Java']}，这不利于处理二级标签，也不便于后续推荐引擎（协同过滤）模块的开发。推荐引擎便利性：协同过滤通常基于用户偏好匹配相似用户/题目。使用嵌套结构（如{"Python": ["Python基础", "Python进阶"]}），你可以：

- 计算用户在二级标签上的相似度（e.g., Jaccard相似度或向量嵌入）。
- 过滤题目：直接用用户选的二级标签查询题库（e.g., WHERE category LIKE 'Python-Python基础'）。
- 扩展性好：未来题库加新一级（如'Java'），前端/后端无缝支持。

故将json对象修改为嵌套checkbox结构

```vue
<label>技术偏好</label>
        <div class="current-preferences">
          <div v-if="selectedPreferences && Object.keys(selectedPreferences).length > 0">
            <div v-for="[group, subs] in Object.entries(selectedPreferences)" :key="group">
              <span class="tag-group">{{ group }}：</span>
              <span v-for="sub in subs" :key="sub" class="tag-item">{{ sub }}</span>
            </div>
          </div>
          <span v-else class="no-tags">暂无技术偏好</span>
        </div>
```

```js
const selectedPreferences = ref({});
const tempSelectedPreferences = ref({}); // 临时存储弹窗中的选择
const showPreferenceModal = ref(false);

// 解析现有的偏好设置，更新选中的复选框
const existingPrefs = response.data.preferences || {};
selectedPreferences.value = {...existingPrefs};
form.preferences = JSON.stringify(selectedPreferences.value);
```



# 题目管理模块

### 添加题目

#### 创建题目模型

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)


class Question(models.Model):
    title = models.CharField(max_length=200)
    answer = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    difficult = models.IntegerField(default=1)  # 1-3 对应 易 中 难
    is_approved = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

创建视图

```python
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Question
from .serializers import CategorySerializer, QuestionSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # 读公开，写需登录


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_approved', 'difficult']
    search_fields = ['title', 'answer']  # 内部搜索字段
    ordering_fields = ['created_at', 'difficulty']

    def perform_create(self, serializer):
        # 创建时添加创建者
        serializer.save(creator=self.request.user)

```



### 过滤后端配置

```python
filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]  # 过滤、搜索、排序
filterset_fields = ['category', 'is_approved', 'difficulty']  # 过滤字段
```

**filter_backends** 用于指定该视图支持哪些过滤后端，本质上是一个过滤器类的列表。

**DjangoFilterBackend** 提供精确字段过滤功能，允许通过 URL 参数进行复杂查询。通过 **filterset_fields** 属性指定可过滤的字段。

**filters.SearchFilter** 提供全文搜索功能，可以在指定字段中搜索关键词。通过 **search_fields** 属性指定搜索的字段。

**filters.OrderingFilter** 提供排序功能，允许按照指定字段进行升序/降序排列。通过 **ordering_fields** 属性指定可排序的字段。



这意味着 API 支持以下类型的请求：

```cmd
过滤：/api/questions/?category=1&difficulty=2
搜索：/api/questions/?search=python
排序：/api/questions/?ordering=-created_at
组合使用：/api/questions/?category=1&search=python&ordering=-created_at
```

这种设计提供了非常灵活的数据检索方式，允许前端根据需要构建复杂的查询条件。







# 答题练习模块























































































































































# 测试

```text
注册
{ 
"username": "test", 
"email": "test@example.com",
"password": "text123"
}

登录
{ 
"username": "test", 
"password": "text123"
}

返回token
{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2ODgzOTQ5NCwiaWF0IjoxNzY4NzUzMDk0LCJqdGkiOiI4M2E3MjU2ZTYyYWQ0MmJlOWRkNmE3ZGUzMzRjOTA2ZCIsInVzZXJfaWQiOiIxIn0.sx2BQXnv7k0SXs6l633kS-CQeZSkTHrSRr8E8mloiYI","access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4NzU2Njk0LCJpYXQiOjE3Njg3NTMwOTQsImp0aSI6ImQ1ODk5NDRlN2IwYjQ2MzRiMjExOTU3ZDIyZWJjYjk5IiwidXNlcl9pZCI6IjEifQ.wM1NmdWefWxBiIs8zHQLe4B-GpOpGapuKvUW7ytdn3o","user":{"id":1,"username":"test","email":"test@example.com","password":"pbkdf2_sha256$1000000$i6ICyov4A0INvd5kV90GBp$rP23QdwZI8U2wHLJRt3jIZVPNCS9iBhZWO5Z5KCI3uM=","preferences":{}}}

Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4NzU2Njk0LCJpYXQiOjE3Njg3NTMwOTQsImp0aSI6ImQ1ODk5NDRlN2IwYjQ2MzRiMjExOTU3ZDIyZWJjYjk5IiwidXNlcl9pZCI6IjEifQ.wM1NmdWefWxBiIs8zHQLe4B-GpOpGapuKvUW7ytdn3o
```



# Git命令

```git
echo "# interview_system" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/iktalk2004/interview_system.git
git push -u origin main

git remote add origin https://github.com/iktalk2004/interview_system.git
git branch -M main
git push -u origin main
```

```
# 1. 如果这个文件夹从来没用过 git，先初始化
git init

# 2. 添加所有文件到暂存区（. 代表全部文件）
git add .

# 3. 第一次提交（必须写提交信息）
git commit -m "初次提交：毕业设计完整项目结构（Django + Vue3）"

# 4. 连接到你刚刚创建的 GitHub 远程仓库
# 把下面这行里的 URL 换成你自己仓库的地址（HTTPS 或 SSH 都可以）
git remote add origin https://github.com/iktalk2004/interview_system.git

# 5. 把本地 main 分支推送到远程（-u 只需第一次用，以后可以直接 git push）
git branch -M main          # 确保当前分支叫 main（GitHub 默认）
git push -u origin main(推荐)


# 修改代码 → 暂存 → 提交 → 推送
git add .
git commit -m "完成了用户管理模块"
git push
```



