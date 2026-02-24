from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'directions', views.DirectionViewSet, basename='direction')
router.register(r'students', views.StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
]