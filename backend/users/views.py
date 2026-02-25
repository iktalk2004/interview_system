from rest_framework import generics, status, parsers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, UserUpdateSerializer, AvatarUploadSerializer
from .models import User
from .models_blacklist import BlacklistedToken
import logging

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class LoginView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    """
    用户资料更新视图
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(UserSerializer(instance).data)


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


class LogoutView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            BlacklistedToken.cleanup_expired()
            
            logger.info(f"User {request.user.username} logged out successfully")
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except TokenError as e:
            logger.warning(f"Logout failed for user {request.user.username}: {str(e)}")
            return Response({"detail": "Token is invalid or already blacklisted."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({"detail": "Logout failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)