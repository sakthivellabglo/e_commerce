from functools import cached_property
from django.db import models
from django.contrib.auth.models import User

FAILED = 0
SUCCESS = 1
PENDING = 2
Order_choices = [
    (PENDING, 'PENDING'),
    (SUCCESS, 'sucess'),
    (FAILED, 'failed'),
]


class TimeStampBaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Brand(models.Model):
    name = models.CharField(max_length=40)
    logo = models.ImageField(upload_to='images/')

    def __str__(self):
        return " {} ".format(self.name)


class Product(TimeStampBaseModel):
    title = models.CharField(max_length=40)
    image = models.ImageField(upload_to='images/')
    price = models.IntegerField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    stock = models.BooleanField(default=True)

    def __str__(self):
        return " {} {} {} {} {} ".format(self.title, self.image, self.price, self.brand, self.stock)


class Cart(TimeStampBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()
    date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return " {} {} {} {} {} ".format(self.user, self.product, self.quantity, self.price, self.date)

class Wishlist(TimeStampBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product)


class Order(TimeStampBaseModel):
    total_price = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Cart)
    order_status = models.IntegerField(
        choices=Order_choices,
        default=PENDING
    )

class Payment(models.Model):
     total_price = models.IntegerField()
     order_id =  models.ForeignKey(Order, on_delete=models.CASCADE)
     payment_status = models.IntegerField(
        choices=Order_choices,
        default=PENDING
    )
     transaction_id = models.CharField(max_length=100)
