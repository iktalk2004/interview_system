from django.db import models
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class BlacklistedToken(models.Model):
    """
    JWT Token 黑名单模型
    用于撤销已登出的 token
    """
    token = models.CharField(max_length=500, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklisted_tokens')
    blacklisted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True, help_text='Token 过期时间')

    class Meta:
        verbose_name = '黑名单 Token'
        verbose_name_plural = '黑名单 Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Token for {self.user.username} (expires at {self.expires_at})"

    @classmethod
    def is_blacklisted(cls, token_jti):
        """
        检查 token 是否在黑名单中
        """
        return cls.objects.filter(token=token_jti).exists()

    @classmethod
    def cleanup_expired(cls):
        """
        清理过期的黑名单 token
        """
        from django.utils import timezone
        deleted_count = cls.objects.filter(expires_at__lt=timezone.now()).delete()[0]
        logger.info(f"Cleaned up {deleted_count} expired blacklisted tokens")
        return deleted_count
