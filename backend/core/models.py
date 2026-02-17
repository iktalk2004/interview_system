from django.db import models
from django.utils import timezone


class SoftDeleteModel(models.Model):
    """
    软删除模型基类
    所有需要软删除功能的模型都应该继承此类
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """
        软删除记录
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """
        恢复已删除的记录
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        """
        重写 delete 方法，使用软删除
        """
        self.soft_delete()

    def hard_delete(self, using=None, keep_parents=False):
        """
        硬删除记录（真正从数据库中删除）
        """
        super().delete(using=using, keep_parents=keep_parents)
