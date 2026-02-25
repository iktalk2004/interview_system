# Generated migration for new models and constraints

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('questions', '0001_initial'),
        ('practice', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlacklistedToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, max_length=500, unique=True)),
                ('blacklisted_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('expires_at', models.DateTimeField(db_index=True, help_text='Token 过期时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blacklisted_tokens', to='users.user')),
            ],
            options={
                'verbose_name': '黑名单 Token',
                'verbose_name_plural': '黑名单 Tokens',
            },
        ),

        migrations.CreateModel(
            name='QuestionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('answer', models.TextField(blank=True)),
                ('explanation', models.TextField(blank=True)),
                ('difficulty', models.IntegerField()),
                ('tags', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('change_reason', models.TextField(blank=True, help_text='修改原因')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='questions.category')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_question_versions', to='users.user')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='questions.question')),
            ],
            options={
                'verbose_name': '题目历史',
                'verbose_name_plural': '题目历史',
                'ordering': ['-version'],
            },
        ),

        migrations.CreateModel(
            name='WrongQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wrong_count', models.IntegerField(default=1, help_text='答错次数')),
                ('last_wrong_at', models.DateTimeField(auto_now=True, help_text='最后一次答错时间')),
                ('last_score', models.FloatField(help_text='最后一次得分')),
                ('mastered', models.BooleanField(default=False, help_text='是否已掌握')),
                ('mastered_at', models.DateTimeField(blank=True, help_text='掌握时间', null=True)),
                ('notes', models.TextField(blank=True, help_text='用户笔记')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wrong_records', to='questions.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wrong_questions', to='users.user')),
            ],
            options={
                'verbose_name': '错题记录',
                'verbose_name_plural': '错题记录',
            },
        ),

        migrations.CreateModel(
            name='UserBehavior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('view', '查看'), ('answer', '答题'), ('favorite', '收藏'), ('share', '分享'), ('search', '搜索'), ('recommend', '推荐')], db_index=True, max_length=20)),
                ('target_type', models.CharField(db_index=True, help_text='目标类型：question/category/user', max_length=50)),
                ('target_id', models.IntegerField(db_index=True, help_text='目标ID')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='额外元数据')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='behaviors', to='users.user')),
            ],
            options={
                'verbose_name': '用户行为',
                'verbose_name_plural': '用户行为',
            },
        ),

        migrations.AlterUniqueTogether(
            name='wrongquestion',
            unique_together={('user', 'question')},
        ),

        migrations.AddConstraint(
            model_name='question',
            constraint=models.CheckConstraint(
                check=models.Q(difficulty__gte=1) & models.Q(difficulty__lte=4),
                name='valid_difficulty_range'
            ),
        ),

        migrations.AddConstraint(
            model_name='question',
            constraint=models.CheckConstraint(
                check=models.Q(avg_score__gte=0) & models.Q(avg_score__lte=100),
                name='valid_avg_score_range'
            ),
        ),

        migrations.AddConstraint(
            model_name='question',
            constraint=models.CheckConstraint(
                check=models.Q(view_count__gte=0),
                name='valid_view_count'
            ),
        ),

        migrations.AddConstraint(
            model_name='interaction',
            constraint=models.CheckConstraint(
                check=models.Q(score__gte=0) & models.Q(score__lte=100),
                name='valid_score_range'
            ),
        ),

        migrations.AddConstraint(
            model_name='interaction',
            constraint=models.CheckConstraint(
                check=models.Q(time_spent__gte=0),
                name='valid_time_spent'
            ),
        ),

        migrations.AddConstraint(
            model_name='interaction',
            constraint=models.CheckConstraint(
                check=models.Q(attempts__gte=1),
                name='valid_attempts'
            ),
        ),
    ]
