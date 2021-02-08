# Generated by Django 3.1.3 on 2021-02-08 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asovi_app', '0012_merge_20210203_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='popular',
            name='place_id',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='latitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='post',
            name='longitude',
            field=models.FloatField(),
        ),
    ]