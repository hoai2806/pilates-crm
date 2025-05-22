from django.urls import path
from . import views

app_name = 'calendar'

urlpatterns = [
    path('', views.CalendarView.as_view(), name='calendar'),
    path('api/events/', views.get_calendar_events, name='calendar_events'),
    path('api/statistics/', views.get_statistics, name='calendar_statistics'),
    path('api/class-types/', views.get_class_types, name='class_types'),
    path('api/instructors/', views.get_instructors, name='instructors'),
    path('api/customers/', views.get_customers, name='customers'),
] 