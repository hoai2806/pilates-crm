from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('customers/', views.customer_dashboard, name='customer_dashboard'),
    path('customers/danh-sach/', views.customer_list, name='customer_list'),
    path('customers/them-moi/', views.customer_add_view, name='customer_add'),
    path('', views.main_dashboard_view, name='main_dashboard'),
    path('customers/khach-hang-chi-tiet/<int:pk>/', views.customer_detail_view, name='customer_detail'),
    path('customers/khach-hang-chi-tiet/<int:pk>/edit', views.customer_edit_view, name='customer_edit'),
    path('instructors/', views.instructor_list, name='instructor_list'),
    path('instructors/them-moi/', views.instructor_form, name='instructor_form'),
    path('instructors/<int:pk>/chinh-sua/', views.instructor_form, name='instructor_edit'),
    path('instructors/<int:pk>/xoa/', views.instructor_delete, name='instructor_delete'),
    path('lop-hoc/', views.classtype_list, name='classtype_list'),
    path('lop-hoc/them-moi/', views.classtype_form, name='classtype_form'),
    path('lop-hoc/<int:pk>/chinh-sua/', views.classtype_form, name='classtype_edit'),
    path('lop-hoc/<int:pk>/xoa/', views.classtype_delete, name='classtype_delete'),
    path('lop-hoc/<int:pk>/nhan-doi/', views.classtype_duplicate, name='classtype_duplicate'),
    path('chi-nhanh/', views.branch_list, name='branch_list'),
    path('chi-nhanh/them-moi/', views.branch_form, name='branch_form'),
    path('chi-nhanh/<int:pk>/chinh-sua/', views.branch_form, name='branch_edit'),
    path('chi-nhanh/<int:pk>/xoa/', views.branch_delete, name='branch_delete'),
    path('nguoi-dung/', views.user_list, name='user_list'),
    path('lich-hoc/', views.class_schedule_calendar, name='class_schedule_calendar'),
    path('lich-hoc/bang/', views.class_schedule_table, name='class_schedule_table'),
    path('lich-hoc/them-moi/', views.class_schedule_form, name='class_schedule_form'),
    path('get-calendar-events/', views.get_calendar_events, name='get_calendar_events'),
    path('api/class-schedule/<int:schedule_id>/delete/', views.delete_class_schedule, name='delete_class_schedule'),
    path('api/appointment/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
    path('api/search-customers/', views.search_customers, name='search_customers'),
    path('goi-tap/', views.package_list, name='package_list'),
    path('goi-tap/them-moi/', views.package_form, name='package_form'),
    path('goi-tap/<int:pk>/chinh-sua/', views.package_form, name='package_edit'),
    path('goi-tap/<int:pk>/xoa/', views.package_delete, name='package_delete'),
    path('don-hang/', views.payment_redirect, name='payment_redirect'),
] 