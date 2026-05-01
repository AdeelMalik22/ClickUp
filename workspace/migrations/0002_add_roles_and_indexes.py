# Generated migration for adding workspace member roles and indexes

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspacemember',
            name='role',
            field=models.CharField(
                choices=[('owner', 'Owner'), ('manager', 'Manager'), ('member', 'Member'), ('guest', 'Guest')],
                default='member',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='workspacemember',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='workspace_memberships',
                to='core.user'
            ),
        ),
        migrations.AlterField(
            model_name='workspace',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='owned_workspaces',
                to='core.user'
            ),
        ),
        migrations.AddIndex(
            model_name='workspace',
            index=models.Index(fields=['created_by', '-created_at'], name='workspace_workspace_created_by_created_idx'),
        ),
        migrations.AddIndex(
            model_name='workspacemember',
            index=models.Index(fields=['workspace', 'user'], name='workspace_workspacemember_workspace_user_idx'),
        ),
        migrations.AddIndex(
            model_name='workspacemember',
            index=models.Index(fields=['workspace', 'role'], name='workspace_workspacemember_workspace_role_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='workspacemember',
            unique_together={('workspace', 'user')},
        ),
    ]

