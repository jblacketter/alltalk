# Generated by Django 5.2.4 on 2025-07-27 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DreamGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_private', models.BooleanField(default=True, help_text='Private groups require invitation')),
                ('requires_approval', models.BooleanField(default=False, help_text='New members need approval')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'dream_groups',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('member', 'Member'), ('moderator', 'Moderator'), ('admin', 'Admin')], default='member', max_length=20)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'group_memberships',
            },
        ),
        migrations.CreateModel(
            name='ShareHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('shared', 'Shared'), ('unshared', 'Unshared'), ('modified', 'Modified Sharing')], max_length=20)),
                ('old_privacy', models.CharField(blank=True, max_length=20)),
                ('new_privacy', models.CharField(blank=True, max_length=20)),
                ('performed_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'share_history',
                'ordering': ['-performed_at'],
            },
        ),
    ]
