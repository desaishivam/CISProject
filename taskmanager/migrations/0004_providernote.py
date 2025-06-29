# Generated by Django 5.2.1 on 2025-06-25 17:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanager', '0003_task_completed_by_alter_task_assigned_to_and_more'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_important', models.BooleanField(default=False, help_text='Mark as important for priority display')),
                ('caregiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_notes', to='users.userprofile')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provider_notes', to='users.userprofile')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_notes', to='users.userprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
