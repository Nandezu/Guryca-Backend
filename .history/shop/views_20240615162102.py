from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create':
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)
