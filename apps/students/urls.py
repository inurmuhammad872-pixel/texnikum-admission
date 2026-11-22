from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, DirectionViewSet
router = DefaultRouter()
router.register('directions', DirectionViewSet, basename='direction')
router.register('students', StudentViewSet, basename='student')
urlpatterns = [path('', include(router.urls))]
