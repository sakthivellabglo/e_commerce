from rest_framework import serializers
from django.contrib.auth.models import User
from .models import(
    Brand,
    Product,
    Cart,
    Order,
    Wishlist
    )

class CreateuserSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password',
                  'email', 'first_name', 'last_name')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create_superuser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class Loginserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'image', 'price', 'brand', 'description', 'stock', 'created_on',
                  'updated_on')
        read_only_fields = ('created_on', 'updated_on')

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'logo')

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('id', 'user', 'product', 'price','quantity',  'date', 'is_active', 'created_on',
                  'updated_on')
        read_only_fields = ('created_on', 'updated_on','date','is_active', 'price')



class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ('id', 'user', 'product')
        read_only_fields = ('created_on', 'updated_on')