import json
import stripe

from rest_framework import generics
from rest_framework .pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from .models import Brand, Cart, Order, Payment, Product, Wishlist
from .serializers import (
    BrandSerializer,
    CartSerializer,
    CreateuserSerializers,
    Loginserializer,
    OrderSerializer,
    PaymentSerializer,
    ProductSerializer,
    WishlistSerializer
)


endpoint_secret = 'whsec_e0a586f0438ef2272488a985e956d2b1b87f3a79cb61f781fc9530ead00c6c04 '
stripe.api_key = 'sk_test_51M0fZUSJedpYswPhm7MNkYmbVQt2jmmZXNROdSaM73KQ11Y7kkJllXki6I1NIvsMR7XLQfisvlrVKXfaozRd5ZHR00VvOF4Vhq'


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class Register(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = CreateuserSerializers


class LoginView(generics.GenericAPIView):
    serializer_class = Loginserializer
    pagination_class = LargeResultsSetPagination

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'})
        user = authenticate(username=username, password=password)

        if not user:
            return Response({'error': 'Invalid Credentials'})
        login(request, user)
        token, li = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class ProductList(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LargeResultsSetPagination


class BrandList(viewsets.ModelViewSet):

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = LargeResultsSetPagination


class CartList(viewsets.ModelViewSet):

    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product = self.request.data['product']
        product = Product.objects.get(id=product)
        quantity = self.request.data['quantity']
        product_price = product.price*int(quantity)
        serializer.save(user=self.request.user,
                        price=product_price)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(user=request.user)
        print("queryset of list", queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CreateDeleteLikeView(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        queryset = self.filter_queryset(self.get_queryset())
        print("the checking propose", queryset)
        subset = queryset.filter(Q(user_id=self.request.data['user']) & Q(
            product=self.request.data['product']))
        if subset.count() > 0:
            subset.first().delete()
            return
        serializer.save()

class OrderList(viewsets.ModelViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = LargeResultsSetPagination


class PaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD payment for an order
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        res = super().get_queryset()
        user = self.request.user
        return res.filter(order_id__user=user)


class StripeCheckoutSessionCreateAPIView(APIView):
    """
    Create and return checkout session ID for order payment of type 'Stripe'
    """

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(Q(user=request.user))
        order_items = []
        orders = Order.objects.create(
            user=request.user)
        orders.items.add(*cart)
        orders.save()

        for order_item in cart:
            print("fbgdfcbhxfgbhfcxb fbdfcxbhfgxcbh fcgbhfgbhfsghfs")
            product = order_item.product
            quantity = order_item.quantity

            data = {
                'price_data': {
                    'currency': 'inr',
                    'unit_amount':  int(product.price * 100),
                    'product_data': {
                        'name': product.title,
                        'description': product.description,
                        'images': [product.image]
                    }
                },
                'quantity': quantity
            }

            order_items.append(data)
            print("jukjuyjkyujty yjtgtyjtyj hutyjtyjty",order_items)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=order_items,
            metadata={
                "order_id": orders.id
            },
            mode='payment',
            success_url="http://127.0.0.1:8000/payment/",
            cancel_url="http://127.0.0.1:8000/payment/"
        )
        Payment.objects.create(
            order_id=orders, transaction_id=checkout_session["id"])
        print(checkout_session.url)
        return Response({'sessionId': checkout_session['id']}, status=status.HTTP_201_CREATED)


class StripeWebhookAPIView(APIView):

    def post(self, request, format=None):
        payload = request.body.decode('utf-8')
        payload = json.loads(payload)

        if payload['type'] == 'checkout.session.completed':
            session = payload['data']['object']

            order_id = session['metadata']['order_id']
            print('Payment successfull')

            payment = get_object_or_404(Payment, order_id=order_id)
            print("thr payment is ", payment)
            payment.payment_status = 1
            payment.save()

            order = get_object_or_404(Order, id=order_id)
            order.order_status = 1
            Cart.objects.all().delete()
            order.save()
        elif payload["type"] == "checkout.session.expired":
            session = payload['data']['object']

            order_id = session['metadata']['order_id']
            print('Payment successfull')

            payment = get_object_or_404(Payment, order_id=order_id)
            print("thr payment is ", payment)
            payment.payment_status = 0
            payment.save()
            Cart.objects.all().delete()

            order = get_object_or_404(Order, id=order_id)
            order.order_status = 0
            order.save()

        return Response(status=status.HTTP_200_OK)
# Create your views here.
