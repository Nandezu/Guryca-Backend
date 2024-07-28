from django.urls import path
from .views import try_on, get_user_try_on_results, delete_try_on_result

urlpatterns = [
    path('try-on/', try_on, name='try-on'),
    path('results/', get_user_try_on_results, name='user-try-on-results'),
    path('delete-result/<int:result_id>/', delete_try_on_result, name='delete-try-on-result'),
]