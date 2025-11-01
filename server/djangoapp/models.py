from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.


class CarMake(models.Model):
    """
    CarMake model to store information about car manufacturers
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    country = models.CharField(max_length=100, default="USA")
    founded_year = models.IntegerField(default=2000)

    class Meta:
        verbose_name_plural = "Car Makes"

    def __str__(self):
        return self.name


class CarModel(models.Model):
    """
    CarModel model to store information about car models
    """
    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        ('COUPE', 'Coupe'),
        ('HATCHBACK', 'Hatchback'),
        ('TRUCK', 'Truck'),
        ('CONVERTIBLE', 'Convertible'),
    ]

    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=15,
        choices=CAR_TYPES,
        default='SEDAN'
    )
    year = models.IntegerField(
        default=2023,
        validators=[
            MinValueValidator(2015),
            MaxValueValidator(2023)
        ]
    )
    features = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "Car Models"

    def __str__(self):
        return f"{self.car_make.name} - {self.name} ({self.year})"
