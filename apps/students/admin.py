from django.contrib import admin
from .models import Student, Direction, Document

@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'quota', 'is_active']
    search_fields = ['name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['fio', 'jshshir', 'status', 'created_at']
    search_fields = ['fio', 'jshshir', 'phone']
    list_filter = ['status', 'direction']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['student', 'uploaded_at']
    search_fields = ['student__fio']