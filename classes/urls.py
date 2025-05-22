from django.urls import path
from . import views
from custom_admin.views import class_session_info

app_name = 'classes'

urlpatterns = [
    path('api/class-price/<int:price_id>/', views.class_price_api, name='class_price_api'),
    path('api/class-prices-by-type/<int:class_type_id>/', views.class_prices_by_type_api, name='class_prices_by_type_api'),
    path('api/class-type/<int:class_type_id>/', views.class_type_api, name='class_type_api'),
    path('api/class_session_info/', class_session_info, name='class_session_info'),
] 