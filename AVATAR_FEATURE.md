# 用户头像功能说明

## 功能概述

本系统实现了完整的用户头像功能，包括：
- 头像上传
- 头像预览
- 头像删除
- 默认头像
- 头像显示组件

## 后端实现

### 1. 数据模型

**文件**: [users/models.py](file:///e:\04_Interview_system\backend\users\models.py)

```python
class User(AbstractUser):
    avatar = models.ImageField(
        upload_to=user_avatar_upload_path,
        blank=True,
        null=True,
        default='avatars/default/default-avatar.png',
        help_text='用户头像'
    )
    
    def get_avatar_url(self):
        """
        获取头像 URL
        """
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/media/avatars/default/default-avatar.png'
```

**字段说明**:
- `avatar`: ImageField 字段，存储用户头像
- `upload_to`: 使用 `user_avatar_upload_path` 函数生成上传路径
- `default`: 默认头像路径
- `get_avatar_url()`: 获取头像 URL 的方法

### 2. 序列化器

**文件**: [users/serializers.py](file:///e:\04_Interview_system\backend\users\serializers.py)

#### UserSerializer
```python
class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'bio', 'preferences', 'avatar', 'avatar_url']

    def get_avatar_url(self, obj):
        """
        获取头像 URL
        """
        return obj.get_avatar_url()
```

#### AvatarUploadSerializer
```python
class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField(
        required=True,
        allow_empty_file=False,
        help_text='用户头像图片'
    )

    def validate_avatar(self, value):
        """
        验证头像文件
        """
        max_size = 2 * 1024 * 1024  # 2MB
        if value.size > max_size:
            raise serializers.ValidationError('头像文件大小不能超过 2MB')

        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError('只支持 JPG、PNG、GIF、WebP 格式的图片')

        return value
```

**验证规则**:
- 文件大小：不超过 2MB
- 文件格式：JPG、PNG、GIF、WebP

### 3. 视图

**文件**: [users/views.py](file:///e:\04_Interview_system\backend\users\views.py)

#### AvatarUploadView
```python
class AvatarUploadView(generics.CreateAPIView):
    """
    头像上传视图
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarUploadSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar_file = serializer.validated_data['avatar']
        user = request.user

        try:
            user.avatar = avatar_file
            user.save()

            logger.info(f"User {user.username} uploaded new avatar")

            return Response({
                'message': '头像上传成功',
                'avatar_url': user.get_avatar_url()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Avatar upload failed for user {user.username}: {e}")
            return Response({
                'error': '头像上传失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

#### AvatarDeleteView
```python
class AvatarDeleteView(generics.DestroyAPIView):
    """
    删除头像视图
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        try:
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = None
            user.save()

            logger.info(f"User {user.username} deleted avatar")

            return Response({
                'message': '头像删除成功',
                'avatar_url': user.get_avatar_url()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Avatar deletion failed for user {user.username}: {e}")
            return Response({
                'error': '头像删除失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### 4. URL 配置

**文件**: [users/urls.py](file:///e:\04_Interview_system\backend\users\urls.py)

```python
urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/avatar/upload/', AvatarUploadView.as_view(), name='avatar-upload'),
    path('profile/avatar/delete/', AvatarDeleteView.as_view(), name='avatar-delete'),
    path('logout/', LogoutView.as_view(), name='logout')
]
```

### 5. 媒体文件配置

**默认头像**: [media/avatars/default/default-avatar.svg](file:///e:\04_Interview_system\backend\media\avatars\default\default-avatar.svg)

SVG 格式的默认头像，包含程序员风格的图标。

## 前端实现

### 1. UserAvatar 组件

**文件**: [components/common/UserAvatar.vue](file:///e:\04_Interview_system\frontend\src\components\common\UserAvatar.vue)

#### Props
| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| user | Object | null | 用户对象 |
| avatarUrl | String | '' | 头像 URL |
| username | String | '' | 用户名 |
| size | String | 'medium' | 头像尺寸（small/medium/large/xlarge） |
| clickable | Boolean | false | 是否可点击 |
| showBadge | Boolean | false | 是否显示徽章 |
| badgeCount | Number | 0 | 徽章数量 |

#### Events
| 事件名 | 参数 | 说明 |
|--------|------|------|
| click | user | 点击头像时触发 |

#### 使用示例
```vue
<template>
  <UserAvatar
    :avatar-url="user.avatar_url"
    :username="user.username"
    size="large"
    :clickable="true"
    @click="handleAvatarClick"
  />
</template>
```

### 2. AvatarUpload 组件

**文件**: [components/common/AvatarUpload.vue](file:///e:\04_Interview_system\frontend\src\components\common\AvatarUpload.vue)

#### Props
| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| avatarUrl | String | '' | 当前头像 URL |
| username | String | '' | 用户名 |

#### Events
| 事件名 | 参数 | 说明 |
|--------|------|------|
| upload-success | avatarUrl | 头像上传成功时触发 |
| delete-success | - | 头像删除成功时触发 |

#### 使用示例
```vue
<template>
  <AvatarUpload
    :avatar-url="user.avatar_url"
    :username="user.username"
    @upload-success="handleAvatarUploadSuccess"
    @delete-success="handleAvatarDeleteSuccess"
  />
</template>
```

### 3. 集成到 Profile 页面

**文件**: [components/Profile.vue](file:///e:\04_Interview_system\frontend\src\components\Profile.vue)

```vue
<template>
  <el-card class="header-card">
    <div class="user-header">
      <div class="avatar-section">
        <AvatarUpload
          :avatar-url="user.avatar_url"
          :username="user.username"
          @upload-success="handleAvatarUploadSuccess"
          @delete-success="handleAvatarDeleteSuccess"
        />
      </div>
      <div class="user-info">
        <h2 class="username">{{ user.username }}</h2>
        <p class="email">{{ user.email }}</p>
        <p class="bio">{{ user.bio || '这个人很懒，什么都没写' }}</p>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import AvatarUpload from './common/AvatarUpload.vue'

const handleAvatarUploadSuccess = (avatarUrl) => {
  user.avatar_url = avatarUrl
  ElMessage.success('头像更新成功')
}

const handleAvatarDeleteSuccess = () => {
  user.avatar_url = ''
  ElMessage.success('头像删除成功')
}
</script>
```

### 4. 集成到 NavBar

**文件**: [components/NavBar.vue](file:///e:\04_Interview_system\frontend\src\components\NavBar.vue)

```vue
<template>
  <el-dropdown trigger="click" @command="handleCommand">
    <div class="user-dropdown">
      <UserAvatar
        :avatar-url="userAvatarUrl"
        :username="userName"
        size="medium"
        :clickable="false"
      />
      <div class="user-info">
        <span class="username code-font">{{ userName }}</span>
        <span class="user-role">{{ isAdmin ? 'admin' : 'user' }}</span>
      </div>
      <el-icon class="arrow-icon"><ArrowDown /></el-icon>
    </div>
  </el-dropdown>
</template>

<script setup>
import UserAvatar from './common/UserAvatar.vue'

const userAvatarUrl = computed(() => {
  return userAvatar.value || '/media/avatars/default/default-avatar.svg'
})
</script>
```

## API 接口

### 1. 上传头像

**接口**: `POST /api/users/profile/avatar/upload/`

**请求头**:
```
Content-Type: multipart/form-data
Authorization: Bearer <access_token>
```

**请求体**:
```
avatar: <file>
```

**响应**:
```json
{
  "message": "头像上传成功",
  "avatar_url": "/media/avatars/user_1/avatar.jpg"
}
```

### 2. 删除头像

**接口**: `DELETE /api/users/profile/avatar/delete/`

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "message": "头像删除成功",
  "avatar_url": "/media/avatars/default/default-avatar.svg"
}
```

### 3. 获取用户信息

**接口**: `GET /api/users/profile/`

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "bio": "这是我的个人简介",
  "avatar": "avatars/user_1/avatar.jpg",
  "avatar_url": "/media/avatars/user_1/avatar.jpg",
  "preferences": {},
  "date_joined": "2026-02-17T00:00:00Z"
}
```

## 配置要求

### 1. Django 设置

在 `settings.py` 中配置媒体文件：

```python
# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# URL 配置
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... 其他 URL 配置
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 2. 前端 API 配置

确保前端 API 配置正确：

```javascript
// src/api/index.js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

export default api
```

## 数据库迁移

### 1. 生成迁移文件

```bash
cd backend
python manage.py makemigrations users
```

### 2. 执行迁移

```bash
python manage.py migrate
```

### 3. 创建默认头像目录

```bash
mkdir -p backend/media/avatars/default
```

## 测试

### 1. 后端测试

```bash
cd backend
python manage.py test users
```

### 2. 前端测试

```bash
cd frontend
npm run test
```

### 3. 手动测试步骤

1. 登录系统
2. 进入个人中心页面
3. 点击头像区域
4. 选择图片文件
5. 预览头像
6. 确认上传
7. 验证头像显示
8. 测试删除头像功能
9. 验证默认头像显示

## 注意事项

1. **文件大小限制**: 头像文件大小不能超过 2MB
2. **文件格式限制**: 只支持 JPG、PNG、GIF、WebP 格式
3. **权限要求**: 上传和删除头像需要用户登录
4. **默认头像**: 用户未上传头像时显示默认头像
5. **图片处理**: 建议在生产环境中使用图片处理服务（如 Pillow、Cloudinary）进行图片压缩和裁剪
6. **存储安全**: 建议在生产环境中使用云存储服务（如 AWS S3、阿里云 OSS）存储媒体文件

## 扩展功能建议

1. **图片裁剪**: 添加图片裁剪功能，让用户裁剪头像
2. **图片压缩**: 自动压缩上传的图片
3. **头像历史**: 保存用户头像历史记录
3. **头像审核**: 添加头像审核功能
4. **头像统计**: 统计头像使用情况
5. **批量上传**: 支持批量上传头像
6. **头像模板**: 提供头像模板供用户选择

## 故障排除

### 问题 1: 头像上传失败

**可能原因**:
- 文件大小超过限制
- 文件格式不支持
- 服务器存储空间不足
- 权限问题

**解决方案**:
- 检查文件大小和格式
- 检查服务器存储空间
- 检查文件权限
- 查看服务器日志

### 问题 2: 头像无法显示

**可能原因**:
- 媒体文件 URL 配置错误
- 静态文件服务未启动
- 文件路径错误

**解决方案**:
- 检查 MEDIA_URL 配置
- 确认静态文件服务正常
- 检查文件路径是否正确

### 问题 3: 默认头像不显示

**可能原因**:
- 默认头像文件不存在
- 文件路径配置错误

**解决方案**:
- 确认默认头像文件存在
- 检查文件路径配置
- 重新上传默认头像文件
