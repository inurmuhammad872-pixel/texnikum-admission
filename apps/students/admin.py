from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Student, Direction, Document


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'quota', 'is_active')
    search_fields = ('name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('fio', 'direction', 'status', 'created_at')
    search_fields = ('fio', 'jshshir', 'phone')
    list_filter = ('status', 'direction')
    readonly_fields = ('consent_at', 'consent_version', 'created_at', 'updated_at')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'uploaded_at', 'private_links')
    search_fields = ('student__fio',)
    readonly_fields = ('private_links',)

    @admin.display(description='Himoyalangan hujjatlar')
    def private_links(self, obj):
        if not obj.pk:
            return '-'
        links = []
        for field, label in [('passport', 'Passport'), ('attestat', 'Attestat'), ('photo', 'Foto')]:
            if getattr(obj, field):
                links.append(format_html('<a href="{}">{}</a>', reverse('private_document', args=(obj.pk, field)), label))
        return mark_safe(' | '.join(str(x) for x in links)) if links else '-'
