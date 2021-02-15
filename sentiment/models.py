from django.db import models
from django.conf import settings

# https://stackoverflow.com/questions/1110153/what-is-the-most-efficient-way-to-store-a-list-in-the-django-models#:~:text=A%20simple%20way%20to%20store%20a%20list%20in,the%20(JSON)%20string%20back%20into%20a%20python%20list.



'''




'''


class Org(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    #user=models.CharField(max_length=10,null=True)
    name=models.CharField(max_length=100)

class Product(models.Model):
    org=models.ForeignKey(Org,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    description=models.CharField(max_length=100)

class Review(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    text=models.CharField(max_length=200)
    polarity=models.FloatField()
    subject=models.FloatField()

class Video(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    data=models.TextField()

class Audio(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    text=models.CharField(max_length=1000)
    polarity=models.FloatField()
    subject=models.FloatField()
