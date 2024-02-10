from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# urls
dealerships_url = "https://ouhaddounour-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
reviews_url = "https://ouhaddounour-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
post_review_url = "https://ouhaddounour-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
# Create your views here.
def about(request):
    '''render about page'''
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

def contact(request):
    '''render contact page'''
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)

def login_request(request):
    '''Handle user login'''
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect(request.path)
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

def logout_request(request):
    '''Logout connected user amd redirect it the main page'''
    logout(request)
    return redirect('djangoapp:index')

def registration_request(request):
    '''Register a new user in the database'''
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        password = request.POST['psw']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username,
                                            first_name=firstname,
                                            last_name=lastname,
                                            password=password
                                            )
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

    else:
        return redirect('djangoapp:signup')

def get_dealerships(request):
    '''get dealers from dealership services api'''
    context = {}
    if request.method == "GET":
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(dealerships_url)
        # add dealership to the context
        context['dealerships'] = dealerships
        return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    '''get dealer reviews from reviews services api and render the reviews of a dealer'''
    context = {}
    if request.method == "GET":
        # Get dealer reviews from the URL
        context['reviews']= get_dealer_reviews_from_cf(reviews_url, dealer_id)
        context['dealer_id'] = dealer_id
        return render(request, 'djangoapp/dealer_details.html', context)

def add_review(request, dealer_id):
    '''add new review using post_request function'''
    context = {}
    if request.method == 'GET':
        dealership = get_dealer_by_id_from_cf(dealerships_url, dealer_id)
        context["dealer_name"] = dealership.short_name
        context["dealer_id"] = dealership.id
        context["cars"] =  CarModel.objects.all()
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == 'POST':
        if request.user.is_authenticated:
            review = {}
            try:
                review["dealership"] = dealer_id
                review["name"] = request.user.username
                review["purchase"] = request.POST.get('purchase', False)
                review["id"] = request.user.id
                review["review"] = request.POST.get('review')
                if review["purchase"]:
                    car_id = request.POST.get('car')
                    car = get_object_or_404(CarModel, pk=car_id)
                    review["purchase_date"] = request.POST.get('purchase_date')
                    review["car_make"] = car.car_make.name
                    review["car_model"] = car.model_name
                    review["car_year"] = car.model_year.strftime("%Y")
            except:
                context["error"] = "input error"
                return render(request, 'djangoapp/add_review.html', context)
            json_payload = {"review" : review}
            try:
                json.dumps(json_payload)
            except (TypeError, ValueError) as e:
                print(f"Error serializing object to JSON: {e}")
            resp = post_request(post_review_url, None, json_payload=json_payload)
            if resp is None:
                return HttpResponse("An internal error occured.", status=500)
            else:
                return redirect('djangoapp:dealer/' + str(dealer_id))
        else:
            return HttpResponse("You must be logged in to add review.", status=403)

