# Generated by Django 3.1.3 on 2021-01-01 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asovi_app', '0014_auto_20210101_1921'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='request_checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='good',
            name='checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reply',
            name='checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='save',
            name='checked',
            field=models.BooleanField(default=False),
        ),
    ]