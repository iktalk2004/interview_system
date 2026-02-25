from django.urls import path
from .views import RegisterView, LoginView, ProfileView, ProfileUpdateView, AvatarUploadView, AvatarDeleteView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/avatar/upload/', AvatarUploadView.as_view(), name='avatar-upload'),
    path('profile/avatar/delete/', AvatarDeleteView.as_view(), name='avatar-delete'),
    path('logout/', LogoutView.as_view(), name='logout')
]

