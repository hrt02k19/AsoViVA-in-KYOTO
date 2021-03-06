# Generated by Django 3.1.3 on 2021-01-08 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asovi_app', '0003_auto_20210104_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='body',
            field=models.TextField(max_length=300),
        ),
        migrations.AlterField(
            model_name='post',
            name='latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='longitude',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='profile',
            name='interested_genre',
            field=models.ManyToManyField(blank=True, to='asovi_app.Genre', verbose_name='興味のあるジャンル'),
        ),
    ]
