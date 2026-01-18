from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes =  [AllowAny]  # 允许任何用户注册
    serializer_class = RegisterSerializer


class LoginView(generics.CreateAPIView):
    permission_classes = [AllowAny]  # 允许任何用户登录
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 验证数据, 如果验证失败，将抛出异常
        user = serializer.validated_data  # 获取验证后的用户对象
        refresh = RefreshToken.for_user(user)  # 创建用户刷新令牌
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,  # 返回用户信息
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class LogoutView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # JWT 无需服务器端注销，客户端删除token即可。这里简单返回成功
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)