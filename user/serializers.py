from rest_framework import serializers
from .models import CustomUser, FavoriteItem
from shop.serializers import ProductSerializer

class CustomUserSerializer(serializers.ModelSerializer):
    active_profile_image = serializers.URLField(read_only=True)
    is_subscription_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'gender', 'shopping_region', 
                  'profile_images', 'active_profile_image', 'subscription_type', 
                  'subscription_start_date', 'subscription_end_date', 
                  'virtual_try_ons_remaining', 'profile_images_remaining', 
                  'try_on_results_remaining', 'is_subscription_active']
        extra_kwargs = {
            'password': {'write_only': True},
            'profile_images': {'read_only': True},
            'subscription_type': {'read_only': True},
            'subscription_start_date': {'read_only': True},
            'subscription_end_date': {'read_only': True},
            'virtual_try_ons_remaining': {'read_only': True},
            'profile_images_remaining': {'read_only': True},
            'try_on_results_remaining': {'read_only': True},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['active_profile_image'] = instance.active_profile_image
        ret['is_subscription_active'] = instance.is_subscription_active
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

class SubscriptionPlanSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.CharField()
    features = serializers.ListField(child=serializers.CharField())
    ai_section = serializers.BooleanField()
    new_section = serializers.BooleanField()

class SubscriptionDetailsSerializer(serializers.Serializer):
    subscription_type = serializers.CharField()
    is_active = serializers.BooleanField()
    end_date = serializers.DateTimeField()
    virtual_try_ons_remaining = serializers.IntegerField()
    profile_images_remaining = serializers.IntegerField()
    try_on_results_remaining = serializers.IntegerField()