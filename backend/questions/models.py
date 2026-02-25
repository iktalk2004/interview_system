from django.db import models
from users.models import User
from core.models import SoftDeleteModel


class Category(SoftDeleteModel):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = '分类'
        verbose_name_plural = '分类'
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['parent', 'order']),
        ]

    def __str__(self):
        return self.name

    def get_full_path(self):
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)


class Question(SoftDeleteModel):
    DIFFICULTY_CHOICES = [
        (1, '简单'),
        (2, '中等'),
        (3, '困难'),
        (4, '专家'),
    ]

    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    content = models.TextField()
    answer = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='questions')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_questions')
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1, db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    is_public = models.BooleanField(default=True, db_index=True)
    explanation = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    view_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    avg_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '题目'
        verbose_name_plural = '题目'
        indexes = [
            models.Index(fields=['title', 'is_approved']),
            models.Index(fields=['category', 'difficulty']),
            models.Index(fields=['difficulty', 'is_approved']),
            models.Index(fields=['is_public', 'is_approved']),
            models.Index(fields=['view_count']),
            models.Index(fields=['avg_score']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(difficulty__gte=1) & models.Q(difficulty__lte=4),
                name='valid_difficulty_range'
            ),
            models.CheckConstraint(
                check=models.Q(avg_score__gte=0) & models.Q(avg_score__lte=100),
                name='valid_avg_score_range'
            ),
            models.CheckConstraint(
                check=models.Q(view_count__gte=0),
                name='valid_view_count'
            ),
        ]

    def __str__(self):
        return self.title

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def increment_answer_count(self):
        self.answer_count += 1
        self.save(update_fields=['answer_count'])

    def update_avg_score(self, new_score):
        total_score = self.avg_score * self.answer_count + new_score
        self.answer_count += 1
        self.avg_score = total_score / self.answer_count
        self.save(update_fields=['avg_score', 'answer_count'])
