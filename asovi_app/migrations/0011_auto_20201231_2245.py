# Generated by Django 3.1.3 on 2020-12-31 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asovi_app', '0010_remove_post_like'),
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