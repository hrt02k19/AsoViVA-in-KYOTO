from django.db.models.deletion import CASCADE, get_candidate_relations_to_delete
from accounts.models import CustomUser
from django.db import models

# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=60)

    class Meta:
        verbose_name_plural = 'genre'

    def __str__(self):
        return self.name

class Profile(models.Model):

    GENDER_CHOICES = [
        (1,'男'),
        (2,'女'),
        (3,'その他'),
    ]

    user = models.OneToOneField(CustomUser,related_name="user_profile",on_delete=CASCADE)
    username = models.CharField(max_length=50)
    icon = models.ImageField(null=True,blank=True)
    introduction = models.TextField(null=True,blank=True)
    interested_genre = models.ManyToManyField(Genre)
    gender = models.IntegerField(choices=GENDER_CHOICES,default=0,null=True,blank=True)

    class Meta:
        verbose_name_plural = 'Profile'
    
    def __str__(self):
        return '<UserProfile:userid=' + str(self.user.id) + ',username=' + self.username + '>'
