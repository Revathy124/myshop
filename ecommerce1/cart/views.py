from http.client import responses

from django.shortcuts import render,redirect
from pyexpat.errors import messages

# Create your views here.
from shop.models import Product
from django.views import View
from cart.models import Cart
class AddtoCart(View):
    def get(self,request,i):
        u=request.user
        p=Product.objects.get(id=i)
        try:
            c=Cart.objects.get(user=u,product=p)
            c.quantity+=1
            c.save()
        except:
            c=Cart.objects.create(user=u,product=p,quantity=1)
            c.save()
        return redirect('cart:cartview')

class CartView(View):
    def get(self,request):
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total+=i.quantity*i.product.price
        return render(request,'cart.html',{'cart':c,'total':total})

class CartDecrementView(View):
    def get(self,request,i):
        u=request.user
        p=Product.objects.get(id=i)
        try:
            c=Cart.objects.get(user=u,product=p)
            if c.quantity>1:
                c.quantity-=1
                c.save()
            else:
                c.delete()
        except:
            pass
        return redirect('cart:cartview')

class CartremoveView(View):
    def get(self,request,i):
        u=request.user
        p=Product.objects.get(id=i)
        try:
            c=Cart.objects.get(user=u,product=p)
            c.delete()
        except:
            pass
        return redirect('cart:cartview')

def check_available(c):
    available=True
    for i in c:
        if i.product.available<i.quantity:
            available=False
            break
    return available
from cart.forms import OrderForm
from cart.models import OrderItems
import razorpay
from django.contrib import messages
class OrderFormView(View):
    def post(self,request):
        data=request.POST
        print(data)
        u=request.user
        #order
        form_instance=OrderForm(request.POST)
        if form_instance.is_valid():
            order_object=form_instance.save(commit=False)
            order_object.user=u
            order_object.save() #creates an order_object in Order Table

            c=Cart.objects.filter(user=u) #cart items selected by particular user
            available=check_available(c)
            if available:
                for i in c:
                    o=OrderItems.objects.create(order=order_object,product=i.product,quantity=i.quantity)
                    o.save()
                    #in each iteration creates an order_items object corresponding to a cart object

                #Order amount
                total=0
                for i in c:
                    total+=i.quantity*i.product.price

                if order_object.payment_method=="ONLINE":

                    #Razorpay Payment
                    #1.creates client connection
                    client=razorpay.Client(auth=('rzp_test_D2f5myhKYLz1wk','by4I9Yo63guGogn5IdtDgfhl'))

                    #2.order creation
                    response_payment=client.order.create(dict(amount=total*100,currency='INR'))

                    #prints the respons
                    print(response_payment)

                    order_id=response_payment['id']
                    order_object.order_id=order_id
                    order_object.is_ordered=False
                    order_object.amount=total
                    order_object.save()
                    return render(request, 'payment.html', {'payment': response_payment, 'name': u.username})


                elif order_object.payment_method=="COD":
                    order_object.is_paid=True
                    order_object.amount=total
                    order_object.save()
                    items=OrderItems.objects.filter(order=order_object)
                    for i in items:
                        i.product.available -= i.quantity
                        i.product.save()
                    c = Cart.objects.filter(user=u)
                    c.delete()
                    return redirect('shop:categories')
                else:
                    pass


            else:
                messages.error(request,"Currently items not available")
                return render(request,'payment.html')
    def get(self,request):
        form_instance=OrderForm()
        return render(request,'orderform.html',{'form':form_instance})

from shop.models import CustomUser
from cart.models import Order
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
@method_decorator(csrf_exempt, name='dispatch') #to avoid csrf protection error

class PaymentsuccessView(View):
    def post(self,request,i):
        user=CustomUser.objects.get(username=i)
        login(request,user)
        response=request.POST # payment confirmation sent by razorpay to our application
                              #order-id, payment-id,signature

        #To change ordered field to True after completion of payment
        print(response)
        o=Order.objects.get(order_id=response['razorpay_order_id'])
        o.is_ordered=True
        o.save()
        items=OrderItems.objects.filter(order=o)
        for i in items:
            i.product.available-=i.quantity
            i.product.save()

        # To delete cart for the current user
        c=Cart.objects.filter(user=user)
        c.delete()
        return render(request,'payment_success.html') #decrement each item in table

class OrderSummaryView(View):
    def get(self,request):
        u=request.user
        o=Order.objects.filter(user=u,is_ordered=True)
        return render(request,'summary.html',{'orders':o})



