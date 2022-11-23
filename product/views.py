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

    def perform_create(self, serializer):
        product= self.request.data['product']
        product =Product.objects.get(id=product)
        quantity = self.request.data['quantity']
        product_price = product.price*int(quantity)
        serializer.save(user=self.request.user, 
                        price = product_price )



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

