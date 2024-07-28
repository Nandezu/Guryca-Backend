from rest_framework import serializers
from .models import TryOnResult

class TryOnResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TryOnResult
        fields = ['id', 'user', 'product', 'result_image', 'created_at']
        read_only_fields = ['user']