from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('them-moi/', views.payment_create, name='payment_create'),
    path('<int:pk>/', views.payment_detail, name='payment_detail'),
    path('<int:pk>/chinh-sua/', views.payment_edit, name='payment_edit'),
    path('export-csv/', views.payment_export_csv, name='payment_export_csv'),
    
    # API endpoint
    path('api/package/<int:package_id>/', views.package_info_api, name='package_info_api'),
    path('api/search-customers/', views.search_customers, name='search_customers'),
    path('api/class-prices/<int:class_type_id>/', views.class_prices_by_type, name='class_prices_by_type'),
] 