# Generated migration for adding priority field and improving indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.CharField(
                choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
                default='medium',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(
                choices=[('todo', 'TODO'), ('in_progress', 'In Progress'), ('review', 'Review'), ('completed', 'Completed'), ('on_hold', 'On Hold'), ('cancelled', 'Cancelled')],
                default='todo',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='task',
            name='assignee',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete='django.db.models.CASCADE',
                to='core.user',
                related_name='task_assignee'
            ),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['project', 'status'], name='project_task_project_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['assignee'], name='project_task_assignee_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['reporter'], name='project_task_reporter_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['priority'], name='project_task_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['workspace', '-created_at'], name='project_project_workspace_created_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['created_by'], name='project_project_created_by_idx'),
        ),
        migrations.AddIndex(
            model_name='taskcomment',
            index=models.Index(fields=['task', '-created_at'], name='project_taskcomment_task_created_idx'),
        ),
        migrations.AddIndex(
            model_name='taskcomment',
            index=models.Index(fields=['user'], name='project_taskcomment_user_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='taskassignee',
            unique_together={('task', 'user')},
        ),
    ]

