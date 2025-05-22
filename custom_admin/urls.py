from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('detail/<str:app_label>/<str:model_name>/<str:object_id>/', views.object_detail_view, name='object_detail'),
    path('api/class_session_info/', views.class_session_info, name='class_session_info'),
    path('api/customer_packages/', views.customer_packages, name='customer_packages'),
] 