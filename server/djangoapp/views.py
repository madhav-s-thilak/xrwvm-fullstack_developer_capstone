# Uncomment the required imports before adding the code

import requests  # ADD THIS LINE at the top with other imports
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
from .models import CarMake, CarModel
from .populate import initiate
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })

    return JsonResponse({"CarModels": cars})
# Create a `login_request` view to handle sign in request


@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request


def logout_request(request):
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)

# Create a `registration` view to handle sign up request


@csrf_exempt
def registration(request):
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except BaseException:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# Update the `get_dealerships` render list of dealerships all by default,
# particular state if state is passed


def get_dealerships(request, state="All"):
    if (state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...
# def get_dealer_reviews(request, dealer_id):
#     # if dealer id has been provided
#     if(dealer_id):
#         endpoint = "/fetchReviews/dealer/"+str(dealer_id)
#         reviews = get_request(endpoint)
#         for review_detail in reviews:
#             response = analyze_review_sentiments(review_detail['review'])
#             print(response)
#             review_detail['sentiment'] = response['sentiment']
#         return JsonResponse({"status":200,"reviews":reviews})
#     else:
#         return JsonResponse({"status":400,"message":"Bad Request"})


def get_dealer_reviews(request, dealer_id):
    """
    Retrieve reviews for a specific dealer from MongoDB
    """
    try:
        # Fetch reviews from MongoDB API
        reviews_url = f"http://localhost:3030/fetchReviews/dealer/{dealer_id}"
        response = requests.get(reviews_url, timeout=5)

        if response.status_code != 200:
            return JsonResponse(
                {"error": "Failed to fetch reviews"}, status=500)

        reviews_data = response.json()
        reviews = []

        for review in reviews_data:
            # Safely get sentiment from sentiment analyzer
            try:
                sentiment_response = requests.get(
                    f"http://sentiment-analyzer:8080/analyze/{review['review']}", timeout=5)

                # Check if response is valid
                if sentiment_response.status_code == 200 and sentiment_response.text:
                    sentiment_data = sentiment_response.json()
                    sentiment = sentiment_data.get('sentiment', 'NEUTRAL')
                else:
                    sentiment = 'NEUTRAL'  # Default sentiment if analysis fails

            except (requests.RequestException, ValueError):
                # If sentiment analyzer fails, use default
                sentiment = 'NEUTRAL'

            review_detail = {
                "id": review.get('id'),
                "name": review.get('name'),
                "dealership": review.get('dealership'),
                "review": review.get('review'),
                "purchase": review.get('purchase'),
                "purchase_date": review.get('purchase_date'),
                "car_make": review.get('car_make'),
                "car_model": review.get('car_model'),
                "car_year": review.get('car_year'),
                "sentiment": sentiment
            }
            reviews.append(review_detail)

        return JsonResponse(reviews, safe=False)

    except Exception as e:
        print(f"Error fetching reviews: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)


# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if (dealer_id):
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

# Create a `add_review` view to submit a review
# def add_review(request):
# ...


def add_review(request):
    if (request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status": 200})
        except BaseException:
            return JsonResponse(
                {"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
