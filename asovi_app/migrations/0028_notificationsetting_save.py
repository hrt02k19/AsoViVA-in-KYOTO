# Generated by Django 3.1.3 on 2021-01-01 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asovi_app', '0027_notificationsetting_friend'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationsetting',
            name='save',
            field=models.BooleanField(default=True, verbose_name='通知設定:保存'),
        ),
    ]
