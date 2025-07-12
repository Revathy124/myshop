from django.contrib import admin

# Register your models here.

from shop.models import Category,Product

admin.site.register(Category)
admin.site.register(Product)


from shop.models import CustomUser
admin.site.register(CustomUser)