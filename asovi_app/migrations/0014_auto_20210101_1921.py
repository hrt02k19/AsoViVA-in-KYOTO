# Generated by Django 3.1.3 on 2021-01-01 10:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asovi_app', '0013_auto_20210101_0215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friend',
            name='request_checked',
        ),
        migrations.RemoveField(
            model_name='good',
            name='checked',
        ),
        migrations.RemoveField(
            model_name='reply',
            name='checked',
        ),
        migrations.RemoveField(
            model_name='save',
            name='checked',
        ),
        migrations.AlterField(
            model_name='save',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='NotificationSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('good', models.BooleanField(default=True, verbose_name='通知設定:いいね')),
                ('save', models.BooleanField(default=True, verbose_name='通知設定:保存')),
                ('reply', models.BooleanField(default=True, verbose_name='通知設定:返信')),
                ('friend', models.BooleanField(default=True, verbose_name='通知設定:フレンドリクエスト')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_notification', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '通知設定',
            },
        ),
    ]