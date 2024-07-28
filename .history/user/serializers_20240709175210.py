from rest_framework import serializers
from .models import CustomUser, FavoriteItem
from shop.serializers import ProductSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'gender', 'shopping_region', 'profile_image', 'profile_image_url']
        extra_kwargs = {
            'password': {'write_only': True},
            'profile_image_url': {'read_only': True},
            'profile_image': {'write_only': True}  # Přidáno pro zajištění, že raw image data nebudou odesílána
        }


    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Zajistíme, že profile_image_url bude vždy součástí odpovědi
        ret['profile_image_url'] = instance.profile_image_url
        return ret


    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user


    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


# Zbytek kódu zůstává nezměněn
class FavoriteItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)


    class Meta:
        model = FavoriteItem
        fields = ['id', 'product', 'created_at']
        read_only_fields = ['user']


class FavoriteItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteItem
        fields = ['product']
