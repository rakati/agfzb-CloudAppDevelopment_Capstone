import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import os


def get_request(url, auth, **kwargs):
    '''A function that fetch data from a remote api and return json results'''
    print("get from {} ".format(url))
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
    try:
        json_data = json.loads(response.text)
        return json_data
    except json.JSONDecodeError:
        print("Failed to parse JSON response")
        return None

def post_request(url, auth, json_payload, **kwargs):
    '''A function that request data from a remote api using post method'''
    print("GET from {} with data: {}".format(url, json_payload))
    headers={'Content-Type': 'application/json'}
    try:
        # Call get method of requests library with URL and parameters
        if auth:
            response = requests.post(url, json=json_payload, headers=headers,
                         auth=HTTPBasicAuth('apikey', auth), params=kwargs)
        else:
            response = requests.post(url, json=json_payload, headers=headers,
                                     params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
        return None
    status_code = response.status_code
    print("With status {} ".format(status_code))
    if status_code != 200:
        return None
    try:
        json_response = response.json()
        print("Post json data:", json.dumps(json_response, indent=4))
        return json_response
    except json.JSONDecodeError:
        print("Failed to parse JSON response")
        return None

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
            review_obj.sentiment=analyze_review_sentiments(review_obj.review)
            results.append(review_obj)
        print("res:", results)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealerreview):
    '''get sentiments of a dealer review'''
    print("text to analyze:", dealerreview)
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