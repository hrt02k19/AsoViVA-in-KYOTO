# Generated by Django 3.1.3 on 2020-12-27 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asovi_app', '0009_remove_post_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='like',
        ),
    ]
