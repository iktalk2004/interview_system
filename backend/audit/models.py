from django.db import models
from users.models import User


class AuditLog(models.Model):
    """
    审计日志模型
    记录所有数据变更历史
    """
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('soft_delete', '软删除'),
        ('restore', '恢复'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    model_name = models.CharField(max_length=100, db_index=True)
    object_id = models.IntegerField(db_index=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name}#{self.object_id} at {self.created_at}"


class AuditLogMixin:
    """
    审计日志混入类
    为模型提供自动记录审计日志的功能
    """
    
    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        import json

        User = get_user_model()
        
        # 获取当前用户（如果有的话）
        current_user = None
        try:
            from django.middleware.common import BrokenLinkEmailsMiddleware
            from threading import local
            if hasattr(local, 'user'):
                current_user = local.user
        except:
            pass

        # 检查是否是创建还是更新
        is_update = hasattr(self, '_loaded_values')
        
        if is_update:
            # 记录更新
            changes = {}
            for field in self._meta.fields:
                if field.name not in ['created_at', 'updated_at']:
                    old_value = getattr(self, f'_loaded_values', {}).get(field.attname)
                    new_value = getattr(self, field.attname)
                    
                    if old_value != new_value:
                        changes[field.name] = {
                            'old': old_value,
                            'new': new_value
                        }
            
            if changes:
                AuditLog.objects.create(
                    user=current_user,
                    model_name=self.__class__.__name__,
                    object_id=self.pk,
                    action='update',
                    changes=changes
                )
        else:
            # 记录创建
            AuditLog.objects.create(
                user=current_user,
                model_name=self.__class__.__name__,
                object_id=self.pk,
                action='create',
                changes={'created': True}
            )

        super().save(*args, **kwargs)
