from django.urls import path
from . import views
from custom_admin.views import customer_packages

urlpatterns = [
    # Các URL hiện có
    
    # Thêm endpoint mới
    path('api/customer_packages/', customer_packages, name='customer_packages'),
] 