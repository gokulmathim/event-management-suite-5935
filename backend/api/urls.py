from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'attendees', views.AttendeeViewSet, basename='attendee')
router.register(r'resources', views.ResourceViewSet, basename='resource')
router.register(r'schedule', views.ScheduleItemViewSet, basename='schedule')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('health/', views.health, name='Health'),
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.CustomObtainAuthToken.as_view(), name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('dashboard/overview/', views.dashboard_overview, name='dashboard-overview'),
    path('', include(router.urls)),
]
