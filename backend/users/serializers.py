from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    """
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'bio', 'preferences', 'avatar', 'avatar_url']

    def get_avatar_url(self, obj):
        """
        获取头像 URL
        """
        return obj.get_avatar_url()


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户更新序列化器
    """
    avatar = serializers.ImageField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    preferences = serializers.JSONField(required=False)

    class Meta:
        model = User
        fields = ['avatar', 'bio', 'preferences']


class AvatarUploadSerializer(serializers.Serializer):
    """
    头像上传序列化器
    """
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


class RegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        """
        重写create方法，实现用户注册逻辑
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        重写validate方法，实现用户登录逻辑
        """
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('用户名或密码错误')
