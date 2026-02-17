from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_user_bio'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(db_index=True, max_length=100)),
                ('object_id', models.IntegerField(db_index=True)),
                ('action', models.CharField(choices=[('create', '创建'), ('update', '更新'), ('delete', '删除'), ('soft_delete', '软删除'), ('restore', '恢复')], db_index=True, max_length=20)),
                ('changes', models.JSONField(default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='users.user')),
            ],
            options={
                'verbose_name': '审计日志',
                'verbose_name_plural': '审计日志',
                'db_table': 'audit_logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
