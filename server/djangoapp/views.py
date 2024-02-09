from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


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

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    '''get dealers from dealership services api'''
    context = {}
    if request.method == "GET":
        url = "https://ouhaddounour-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    '''get dealer reviews from reviews services api and render the reviews of a dealer'''
    context = {}
    if request.method == "GET":
        url = "https://ouhaddounour-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
        # Get dealer reviews from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context['dealer_id'] = dealer_id
        context['reviews']= [str(review) for review in reviews]
        return HttpResponse(json.dumps(context, indent=4), content_type='application/json')

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

