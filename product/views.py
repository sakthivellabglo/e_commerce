from rest_framework import generics
from rest_framework .pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect, reverse
from rest_framework.views import APIView
import stripe

from django.db.models import Q
from .models import Brand, Cart, Product, Wishlist
from django.contrib.auth.models import User
from .serializers import (
    BrandSerializer,
    CartSerializer,
    CreateuserSerializers,
    Loginserializer,
    ProductSerializer,
    WishlistSerializer
)
from django.contrib.auth import authenticate, login


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


class BrandList(viewsets.ModelViewSet):

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class CartList(viewsets.ModelViewSet):

    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter((Q(user=request.user)))
        print("queryset of list", queryset)

        for tweet in queryset:
            print(tweet.id)
            cart = Cart.objects.get(id=tweet.id)
            tweet.price = cart.product.price
            tweet.save()

        page = self.paginate_queryset(queryset)
        print("return the iteralble queryset", page)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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

class StripeCheckOutView(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    def create(self, request):
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID  of the product you want to sell
                        'price_data': {
                              'currency': 'inr',
                              'unit_amount': request.POST['price'],
                               'product_data': {'name': "Product"}, 
                              'quantity': 1
                           }
                        },
                         ],
                         mode='payment',
                         )
                         
            return redirect(checkout_session.url)
        except: 
            return
# Create your views here.
