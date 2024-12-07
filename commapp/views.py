from operator import sub
from django.db.models import Count,Q
from django.shortcuts import render,redirect,get_object_or_404
from urllib import request
from django.http import HttpResponse,JsonResponse
from django.views import View
import razorpay
from razorpay.errors import BadRequestError

from commapp.models import Product
from commapp.forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from commapp.models import Customer,Cart
from django.conf import settings

# Create your views here.
def home(request):
    return render(request,"home.html",{})

def about(request):
    return render(request,"about.html",{})

def contact(request):
    return render(request,"contact.html",{})

class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"category.html",locals())
    
    
class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request,"category.html",locals())
    

class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"productdetail.html",locals())
        
        
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request,'customerregistration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulation! User Register Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'customerregistration.html',locals())
    
    
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request, 'profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            
            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congratulation! Profile Save Successfully')
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request, 'profile.html',locals())
    
    
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'address.html',locals())

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulation! Profile Updated Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")

# def add_to_cart(request):
#     user = request.user
#     product_id = request.GET.get('prod_id')
#     product = Product.objects.get(id=product_id)
#     Cart(user=user,product=product).save()
#     return redirect("/cart")


def add_to_cart(request):
    if request.method == 'GET':
        product_id = request.GET.get('prod_id')
        
        # Ensure the product exists
        product = get_object_or_404(Product, id=product_id)
        user = request.user
        
        # Check if the product is already in the cart
        cart_item, created = Cart.objects.get_or_create(user=user, product=product)
        
        if not created:
            messages.info(request, "This product is already in your cart.")
        else:
            messages.success(request, "Product added to cart successfully.")
        
        return redirect('/cart')  # Redirect to the cart page
    
    return redirect('/')  # Redirect to home page or a fallback route

    

# def show_cart(request):
#     user = request.user
#     cart = Cart.objects.filter(user=user)
#     amount = 0
#     for p in cart:
#         value = p.quantity * p.product.discounted_price
#         amount = amount + value
#     totalamount = amount + 40
    
#     return render(request, 'addtocart.html',locals())

# from django.shortcuts import render
# from .models import Cart

SHIPPING_CHARGE = 40  # Define a constant for the shipping charge

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    
    # Calculate the amount
    amount = sum(item.quantity * item.product.discounted_price for item in cart)
    
    # Add shipping charge if the cart is not empty
    totalamount = amount + SHIPPING_CHARGE if amount > 0 else 0

    # Prepare the context
    context = {
        'cart': cart,
        'amount': amount,
        'totalamount': totalamount,
    }

    return render(request, 'addtocart.html', context)

# class checkout(View):
#     def get(self,request):
#         user = request.user
#         add = Customer.objects.filter(user=user)
#         cart_items = Cart.objects.filter(user=user)
#         famount = 0
#         for p in cart_items:
#             value = p.quantity * p.product.discounted_price
#             famount = famount + value
#         totalamount = famount + 40
#         razoramount = int(totalamount * 100)
#         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
#         data = { "amount":razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
#         payment_response = client.order.create(data=data)
#         print(payment_response)
#         return render(request,'checkout.html',locals())



class Checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)

        # Calculate final amount
        famount = sum(p.quantity * p.product.discounted_price for p in cart_items)
        totalamount = famount + 40  # Add shipping charges
        razoramount = int(totalamount * 100)  # Convert to paise for Razorpay

        # Initialize Razorpay Client
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

        try:
            # Create a Razorpay order
            data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
            payment_response = client.order.create(data=data)

            # Extract the order ID
            order_id = payment_response.get("id")

            # Prepare context for rendering the checkout page
            context = {
                "add": add,
                "cart_items": cart_items,
                "totalamount": totalamount,
                "razoramount": razoramount,
                "order_id": order_id,
            }
            print(context,"context")
            return render(request, "checkout.html", context)

        except BadRequestError as e:
            # Handle invalid requests
            return render(request, "error.html", {"message": f"Razorpay Error: {str(e)}"})

        except Exception as e:
            # Catch all other exceptions
            return render(request, "error.html", {"message": f"An unexpected error occurred: {str(e)}"})
    
def error(request):
    return render(request, "error.html", {"message": "An error occurred."})

# def plus_cart(request):
#     if request.method == 'GET':
#         prod_id = request.GET['prod_id']
#         c = Cart.objects.get(Q(Product=prod_id) & Q(user=request.user))
#         c.quantity+=1
#         c.save()
#         user = request.user
#         cart = Cart.objects.filter(user=user)
#         for p in cart:
#             value = p.quantity * p.product.discounted_price
#             amount = amount + value
#         totalammount = amount + 40
#         data={
#             'quantity':c.quantity,
#             'amount':amount,
#             'totalamount':totalamount # type: ignore
#         }
#         return JsonResponse(data)

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')  # Safely get prod_id
        try:
            # Fetch the cart item
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            c.quantity += 1
            c.save()

            # Calculate amounts
            user = request.user
            cart = Cart.objects.filter(user=user)
            amount = sum(item.quantity * item.product.discounted_price for item in cart)
            totalamount = amount + 40  # Shipping charges

            # Prepare response
            data = {
                'quantity': c.quantity,
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')  # Safely get prod_id
        try:
            # Fetch the cart item
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            if c.quantity > 1:
                c.quantity -= 1
                c.save()
            else:
                c.delete()  # If quantity is 1, remove the cart item

            # Calculate amounts
            user = request.user
            cart = Cart.objects.filter(user=user)
            amount = sum(item.quantity * item.product.discounted_price for item in cart)
            totalamount = amount + 40  # Shipping charges

            # Prepare response
            data = {
                'quantity': c.quantity if c.quantity > 0 else 0,  # Send 0 if the item was removed
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)



def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')  # Safely get prod_id
        try:
            # Remove the cart item for the current user
            cart_item = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            cart_item.delete()

            # Recalculate the cart totals
            cart = Cart.objects.filter(user=request.user)
            amount = sum(item.quantity * item.product.discounted_price for item in cart)
            totalamount = amount + 40 if amount > 0 else 0  # Add shipping charges if cart isn't empty

            # Prepare the JSON response
            data = {
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)

        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)
