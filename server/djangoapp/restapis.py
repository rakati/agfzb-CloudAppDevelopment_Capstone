import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import os


def get_request(url, auth, **kwargs):
    '''A function that fetch data from a remote api and return json results'''
    print("Post to {} ".format(url))
    headers={'Content-Type': 'application/json'}
    try:
        # Call get method of requests library with URL and parameters
        if auth:
            response = requests.get(url, params=kwargs, headers=headers,
                                    auth=HTTPBasicAuth('apikey', auth))
        else:
            response = requests.get(url, headers=headers, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def post_request(url, auth, data):
    '''A function that request data from a remote api using post method'''
    print("GET from {} with data: {}".format(url, data))
    headers={'Content-Type': 'application/json'}
    try:
        # Call get method of requests library with URL and parameters
        if auth:
            response = requests.post(url, json=json_data, headers=headers,
                         auth=HTTPBasicAuth('apikey', auth))
        else:
            response = requests.post(url, json=json_data, headers=headers)
    except:
        # If any error occurs
        print("Network exception occurred")
        return None
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_resp = json.loads(response.text)
    print("Post json data:", json.dumps(json_resp, indent=4))
    return json_resp

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def get_dealers_from_cf(url, **kwargs):
    '''
    the function request data from dealers api service using `get_request`
    function, parse return json data into a CarDealer object list

    Parameters:
    ----------
        url: str
            url of the api service to fetch data from using get method.
        **kargs:
            parameters to use in the query string withing request url
    
    Returns:
    --------
        parsed json result stored in a list of CarDealer objects
    '''
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, None, **kwargs)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            print("DEaler",dealer_doc)
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"],
                                   city=dealer_doc["city"],
                                   full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"],
                                   lat=dealer_doc["lat"],
                                   long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"],
                                   zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

def get_dealer_by_id_from_cf(url, dealerId):
    '''return list with the dealer if found otherwise empty list'''
    return get_dealers_from_cf(url, id=dealerId)

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
    '''
    the function request data from reviews api service using `get_request`
    function, parse return json data into a DealerReview object list

    Parameters:
    ----------
        url: str
            url of the api service to fetch data from using get method.
        **kargs:
            parameters to use in the query string withing request url
    
    Returns:
    --------
        parsed json result stored in a list of DealerReview objects
    '''
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, None, id=dealer_id)
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result
        
        # For each review object
        for review in reviews:
            # Get its content in `doc` object
            review_doc = review
            print("review", review_doc)
            # Create a DealerReview object with values in `doc` object
            review_obj = DealerReview(dealership=review_doc.get("dealership", None),
                                   name=review_doc.get("name", None),
                                   purchase=review_doc.get("purchase", None),
                                   id=review_doc.get("id", None),
                                   review=review_doc.get("review", None),
                                   purchase_date=review_doc.get("purchase_date", None),
                                   car_make=review_doc.get("car_make", None),
                                   car_model=review_doc.get("car_model", None),
                                   car_year=review_doc.get("car_year", None),
                                   sentiment=None)
            sentiment=analyze_review_sentiments(review_obj.review)
            results.append(review_obj)
        print("res:", results)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealerreview):
    '''get sentiments of a dealer review'''
    api_key = os.environ["NLU_KEY"]
    api_url = os.environ["NLU_URL"] + "/v1/analyze?version=2019-07-12"
    data = {
        'text': dealerreview,
        'features': {
            'sentiment': {"document": True}
        }
    }
    json_resp = post_request(api_url, api_key, data) 
    if json_resp is None:
        return None
    return json_resp["sentiment"]["document"]["label"]

# def analyze_review_sentiments(dealerreview):
#     body = {"text": dealerreview, "features": {"sentiment": {"document": True}}}
#     print(dealerreview)
#     response = requests.post(
#         os.environ["NLU_URL"] + "/v1/analyze?version=2019-07-12", # watson_url
#         headers={"Content-Type": "application/json"},
#         json=body,  # Use json parameter for automatic conversion
#         auth=HTTPBasicAuth("apikey", os.environ["NLU_KEY"]), # watson_api_key
#     )

#     # Check if request was successful
#     if response.status_code == 200:
#         sentiment = response.json()["sentiment"]["document"]["label"]
#         print("sentiment:", sentiment)
#         return sentiment
#     return "N/A"