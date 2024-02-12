from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models

# from .restapis import related methods
from .models import CarModel, CarDealer
from .restapis import get_dealers_from_cf,get_dealer_by_id,get_dealer_by_id_from_cf,get_dealer_reviews_from_cf,post_request 

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')
# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successfully!")
            return redirect('djangoapp:index')
        else:
            messages.warning(request, "Invalid username or password.")
            return redirect("djangoapp:index")
# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print("Log out the user '{}'".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']  # Corrected the form field name
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user_exist = User.objects.filter(username=username).exists()
        
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect('djangoapp:index')  # Use the namespace instead of the URL
        else:
            messages.error(request, 'Username already exists. Please choose a different one.')
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url="https://divyasrivemu-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request,dealer_id):
     if request.method == "GET":
         context = {}
         dealer_url = "https://divyasrivemu-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
         dealer = get_dealer_by_id_from_cf(dealer_url, id = dealer_id)
         context['dealer'] = dealer

         review_url = "https://divyasrivemu-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
         reviews = get_dealer_reviews_from_cf(review_url, id = dealer_id)
         context["reviews"] = reviews
         if not context["reviews"] :
            messages.warning(request, "There are no reviews at the moment !!!")   
         return render(request, 'djangoapp/dealer_details.html', context)
def get_dealer_details1(request, dealer_id):
     if request.method == "GET":
         context = {}
         dealer_url = "https://divyasrivemu-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews?id=13"
         dealer = get_dealer_by_id(dealer_url, id=id)
         context['dealer'] = dealer
         if not context["dealer"] :
            messages.warning(request, "There are no dealer at the moment !!!")   
         return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, id):
    context = {}
    dealer_url = "https://divyasrivemu-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
    
    # Get dealer information
    dealer = get_dealer_by_id_from_cf(dealer_url, id)
    context["dealer"] = dealer
    
    if request.method == 'GET':
        # Get cars for the dealer
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            car_id = request.POST.get("car")
            
            # Get car information
            car = CarModel.objects.get(pk=car_id)
        
            # Prepare payload for the review
            payload = {
                "dealership": id,
                "name": username,
                "purchase": request.POST.get("purchasecheck") == 'on',
                "review": request.POST.get("content"),
                "purchase_date": request.POST.get("purchasedate"),
                "car_make": car.make.name,
                "car_model": car.name,
                "car_year": int(car.year.strftime("%Y")),
                "id": id,
                "time": datetime.utcnow().isoformat()
            }
            
            # Prepare payload for the API request
            # new_payload = {"review": payload}
            review_post_url = "https://divyasrivemu-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            
            # Make the POST request
            post_request(review_post_url, payload, id=id)
            
            return redirect("djangoapp:dealer_details", dealer_id=id)
        else:
            # Handle the case where the user is not authenticated
            messages.warning(request, "New review not added. Please log in to add a review !!")
            return redirect('djangoapp:index')
