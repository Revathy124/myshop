from django import forms

from django.contrib.auth.models import User
from shop.models import CustomUser

from django.contrib.auth.forms import UserCreationForm
class SignupForm(UserCreationForm):

    class Meta:
        model=CustomUser
        fields=['username','password1','password2','email','first_name','last_name']

class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)

from shop.models import Category,Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields='__all__'

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['name','image','price','available','category']


