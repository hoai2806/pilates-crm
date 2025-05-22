from django.urls import path
from . import views

app_name = 'reback'

urlpatterns = [
    path('', views.index, name='index'),
    path('customers/', views.customers, name='customers'),
    path('customers/add/', views.customer_add_view, name='customer_add'),
    path('customers/<int:pk>/', views.customer_detail_view, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit_view, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete_view, name='customer_delete'),
    path('schedules/', views.schedules, name='schedules'),
    path('payments/', views.payments, name='payments'),
    path('instructors/', views.instructors, name='instructors'),
    # Thêm các URL khác của theme ở đây
] 