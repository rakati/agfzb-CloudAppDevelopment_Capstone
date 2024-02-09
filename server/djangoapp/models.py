from django.db import models
from django.utils.timezone import now


class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30)
    description = models.CharField(null=False, max_length=200)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    dealer_id = models.IntegerField()
    model_name = models.CharField(null=False, max_length=30)
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'WAGON'
    MODEL_TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'WAGON')
    ]
    model_type = models.CharField(
        null=False,
        max_length=5,
        choices=MODEL_TYPE_CHOICES,
        default=SEDAN
    )
    model_year = models.DateField()

    def __str__(self):
        return str(self.car_make) + "-" + self.model_name + ":" +\
        self.model_type + " model, " + "released in " +\
        str(self.model_year.year)

class CarDealer:
    '''A plain class to hold information about Car dealer'''

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

class DealerReview:
    '''A simple plain class to hold information of a dealer review'''

    def __init__(self, dealership, name, purchase, id, review,
                 purchase_date, car_make, car_model, car_year,
                 sentiment):
        # reviewer dealership
        self.dealership = dealership
        # reviewer name
        self.name = name
        # purchase
        self.purchase = purchase
        # review id
        self.id = id
        # review
        self.review = review
        # Car purchase date
        self.purchase_date = purchase_date
        # reviewed Car Make
        self.car_make = car_make
        # reviewed Car Model
        self.car_model = car_model
        # reviewed Car released year
        self.car_year = car_year
        # review sentiment
        self.sentiment = sentiment

    def __str__(self):
        return self.review