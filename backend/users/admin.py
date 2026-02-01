from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 在基础UserAdmin的基础上添加自定义字段
    list_display = UserAdmin.list_display + ('bio', 'preferences')
    list_filter = UserAdmin.list_filter + ('bio',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'preferences')}),
    )
