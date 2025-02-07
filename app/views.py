from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from .forms import ContactForm, EnquiryForm, SignUpForm
from django.utils.timezone import now
from .models import Product
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.renderers import JSONRenderer

# Create your views here.
def home(request):
    if request.method == 'POST':
        # form = ContactForm(request.POST)
        form =  EnquiryForm(request.POST)
        if form.is_valid():

            if request.user.is_authenticated:
                form.instance.user = request.user
            form.save()
            # Process the form data
            # name = form.cleaned_data['name']
            # email = form.cleaned_data['email']
            # message = form.cleaned_data['message']
            # You can save the data to a database or perform other actions here
            # return JsonResponse({'success': True, 'message': 'Form submitted successfully!'})
            return render(request, 'home.html', {'form': form,})
        else:
            # return JsonResponse({'success': False, 'errors': form.errors})
            return render(request, 'home.html', {'form': form})
    
    # form = ContactForm()
    form = EnquiryForm()

    return render(request, 'home.html', {'form': form})

def about(request):
    print("About")
    return render(request, 'about.html', {'name': 'MicroDegree'})

def contact(request):
    return render(request, 'contact.html')

@login_required(login_url='signin')
def products(request):
    products = Product.objects.all().values('name')  # Converts QuerySet to a list of dictionaries

    # return JsonResponse(list(products), safe=False)
    return render(request, 'products.html')

def category(request, category_slug):
    return render(request, 'category.html', {'category_slug': category_slug})


def product(request, category_slug, product_slug):
    return render(request, 'product.html', { 'category_slug': category_slug, 'product_slug': product_slug})

def cart(request):
    return render(request, 'cart.html')

def checkout(request):
    return render(request, 'checkout.html')

def sign_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username, password)

        user = authenticate(request, username=username, password=password) # Checks for valid credentials

        if user is not None:
            login(request, user) # Creates login session
            return redirect('home')
        
        messages.error(request, 'Invalid username or password')
        return redirect('signin')
    return render(request, 'sign-in.html')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signin')
        
        return render(request, 'sign-up.html', {'form': form})

    form = SignUpForm()
    return render(request, 'sign-up.html', {'form': form})

def sign_out(request):
    logout(request) # Destroys the login session
    return redirect('home')

@login_required(login_url='signin')
def profile(request):
    return render(request, 'profile.html', {"user": request.user})

def profile_update(request):
    return render(request, 'profile-update.html')

def profile_change_password(request):
    return render(request, 'profile-change-password.html')


def profile_address(request):
    return render(request, 'profile-address.html')

def profile_order(request):
    return render(request, 'profile-order.html')


def profile_orders_by_year(request, year):
    return JsonResponse({'year': year})

def profile_order_detail(request, order_id):
    return render(request, 'profile-order-detail.html', {'order_id': order_id})


def employee_details(request, emp_id=None):
    return HttpResponse(f"Details of employee {emp_id}")
