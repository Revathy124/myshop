from django.contrib import admin

# Register your models here.
from cart.models import Cart,OrderItems,Order

admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItems)