from django.urls import path
from .views import try_on, get_user_try_on_results

urlpatterns = [
    path('try-on/', try_on, name='try-on'),
    path('results/', get_user_try_on_results, name='user-try-on-results'),
]