# Generated by Django 3.1.3 on 2021-01-21 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asovi_app', '0011_auto_20201227_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='place_id',
            field=models.TextField(null=True),
        ),
    ]