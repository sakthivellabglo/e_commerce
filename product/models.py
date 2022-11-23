from functools import cached_property
from django.db import models
from django.contrib.auth.models import User

PENDING = 'P'
COMPLETED = 'C'
FAILED = 'F'


STATUS_CHOICES = ((PENDING, ('pending')), (COMPLETED,
                      ('completed')), (FAILED, ('failed')))


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
   
    buyer = models.ForeignKey(
        User, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        ordering = ('-created_on', )

    def __str__(self):
        return self.buyer.get_full_name()

    @cached_property
    def total_cost(self):
        """
        Total cost of all the items in an order
        """
        return round(sum([order_item.cost for order_item in self.order_items.all()]), 2)


class OrderItem(TimeStampBaseModel):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="product_orders", on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        ordering = ('-created_on', )

    def __str__(self):
        return self.order.buyer

    @cached_property
    def cost(self):
        """
        Total cost of the ordered item
        """
        return round(self.quantity * self.product.price, 2)
    
class Payment(TimeStampBaseModel):
 
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=PENDING)
    order = models.OneToOneField(
        Order, related_name='payment', on_delete=models.CASCADE)
    class Meta:
        ordering = ('-created_on', )

    def __str__(self):
        return self.order.buyer
