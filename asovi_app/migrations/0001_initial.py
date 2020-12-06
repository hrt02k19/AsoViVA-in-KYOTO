<<<<<<< HEAD
# Generated by Django 3.1.3 on 2020-12-03 10:47

from django.db import migrations, models
=======
# Generated by Django 3.1.3 on 2020-12-04 09:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
>>>>>>> a7e87619b64dda87adf9f25b7252d9c09c146f55


class Migration(migrations.Migration):

    initial = True

    dependencies = [
<<<<<<< HEAD
=======
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
>>>>>>> a7e87619b64dda87adf9f25b7252d9c09c146f55
    ]

    operations = [
        migrations.CreateModel(
<<<<<<< HEAD
            name='post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images')),
                ('time', models.DateTimeField(null=True)),
                ('body', models.CharField(max_length=300, unique=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
        ),
=======
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='')),
                ('introduction', models.TextField(blank=True, null=True)),
                ('gender', models.IntegerField(blank=True, choices=[('男', 1), ('女', 2), ('その他', 3)], default=0, null=True)),
                ('interested_genre', models.ManyToManyField(to='asovi_app.Genre')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Profile',
            },
        ),
>>>>>>> a7e87619b64dda87adf9f25b7252d9c09c146f55
    ]