from django.db import models



# Create y
class post(models.Model):
    image=models.ImageField(upload_to="images")
    time=models.DateTimeField(null=True)
    body=models.CharField(max_length=300,unique=True)
    latitude=models.FloatField(null=True,blank=True)
    longitude=models.FloatField(null=True,blank=True)



