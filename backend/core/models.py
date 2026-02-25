from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """
    软删除管理器
    默认只返回未删除的记录
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        """
        返回所有记录（包括已删除的）
        """
        return super().get_queryset()

    def deleted_only(self):
        """
        只返回已删除的记录
        """
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteModel(models.Model):
    """
    软删除模型基类
    所有需要软删除功能的模型都应该继承此类
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

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
