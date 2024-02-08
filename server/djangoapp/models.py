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

# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
