# Generated by Django 3.1.3 on 2021-01-01 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asovi_app', '0029_auto_20210102_0022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notificationsetting',
            old_name='saved',
            new_name='has_saved',
        ),
    ]