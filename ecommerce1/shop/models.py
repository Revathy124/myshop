from django.db import models
from django.contrib.auth.models import AbstractUser
from random import randint

# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=20)
    description=models.TextField()
    image=models.ImageField(upload_to="categories")
    def __str__(self):
        return self.name

class Product(models.Model):
    name=models.CharField()
    image=models.ImageField(upload_to="products")
    desc=models.TextField()
    price=models.IntegerField()
    available=models.IntegerField(null=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now_add=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name="products")

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    # phone=models.IntegerField()
    is_verified = models.BooleanField(default=False)  # After verification it will set to true
    otp = models.CharField(max_length=10, null=True, blank=True)  # To store the generated otp in backend table

    def generate_otp(self):
        #for creating random otp number for verification

        otp_number=str(randint(1000,9999))+str(self.id)
        self.otp=otp_number
        self.save()