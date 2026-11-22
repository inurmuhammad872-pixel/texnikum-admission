from django.contrib import admin
from django.urls import path, include
from django.db import connection
from django.http import JsonResponse
from . import web_views


def healthz(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('', web_views.apply, name='apply'),
    path('muvaffaqiyatli/', web_views.success, name='success'),
    path('maxfiylik/', web_views.privacy, name='privacy'),
    path('healthz/', healthz, name='healthz'),
    path('admin/document/<uuid:pk>/<str:field>/', web_views.private_document, name='private_document'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.students.urls')),
]
