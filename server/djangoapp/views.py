import requests
import logging
import json
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


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


@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    response_data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(response_data)


def logout_request(request):
    logout(request)  # Terminate user session
    response_data = {"userName": ""}  # Return empty username
    return JsonResponse(response_data)


@csrf_exempt
def registration(request):
    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except Exception:
        # If not, simply log this is a new user
        logger.debug(f"{username} is new user")

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
        response_data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(response_data)
    else:
        response_data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(response_data)


def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    """
    Retrieve reviews for a specific dealer from MongoDB
    """
    try:
        # Fetch reviews from MongoDB API
        reviews_url = (
            f"http://localhost:3030/fetchReviews/dealer/{dealer_id}"
        )
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
                    f"http://sentiment-analyzer:8080/analyze/{review['review']}",
                    timeout=5)

                # Check if response is valid
                if (sentiment_response.status_code == 200 and
                        sentiment_response.text):
                    sentiment_data = sentiment_response.json()
                    sentiment = sentiment_data.get('sentiment', 'NEUTRAL')
                else:
                    sentiment = 'NEUTRAL'  # Default sentiment if fails

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
        return JsonResponse(
            {"error": "Internal server error"}, status=500)


def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{str(dealer_id)}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def add_review(request):
    """Add a new review for a dealer"""
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception:
            return JsonResponse(
                {"status": 401, "message": "Error in posting review"}
            )
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
