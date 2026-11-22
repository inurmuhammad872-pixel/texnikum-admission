import hashlib
import os
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from apps.students.forms import ApplicationForm
from apps.students.models import Document, Direction


def _rate_limited(request):
    # Best-effort safeguard; switch to a shared cache/CAPTCHA in real production.
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    digest = hashlib.sha256(ip.encode('utf-8')).hexdigest()
    key = 'admission-post-' + digest
    if cache.add(key, 1, timeout=3600):
        return False
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=3600)
        count = 1
    return count > 12


@never_cache
@require_http_methods(['GET', 'POST'])
def apply(request):
    if request.method == 'POST':
        if not settings.ADMISSIONS_OPEN:
            return HttpResponse('Qabul hozircha ochilmagan.', status=503)
        if _rate_limited(request):
            return HttpResponse('Juda ko\'p so\'rov yuborildi. Keyinroq urinib ko\'ring.', status=429)
        form = ApplicationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    student = form.save(commit=False)
                    student.consent_at = timezone.now()
                    student.consent_version = 'v1'
                    student.save()
                    Document.objects.create(student=student)
            except IntegrityError:
                form.add_error('jshshir', 'Bu JSHSHIR bilan ariza allaqachon mavjud.')
            else:
                request.session['submitted_application_id'] = str(student.pk)
                return redirect('success')
    else:
        form = ApplicationForm()
    return render(request, 'admissions/home.html', {
        'form': form,
        'directions_count': Direction.objects.filter(is_active=True).count(),
        'admissions_open': settings.ADMISSIONS_OPEN,
    })


@never_cache
@require_http_methods(['GET'])
def success(request):
    return render(request, 'admissions/success.html', {
        'application_id': request.session.pop('submitted_application_id', None),
    })


@require_http_methods(['GET'])
def privacy(request):
    return render(request, 'admissions/privacy.html')


@staff_member_required
@require_http_methods(['GET'])
def private_document(request, pk, field):
    if not request.user.has_perm('students.view_document'):
        raise PermissionDenied
    if field not in ('passport', 'attestat', 'photo'):
        raise Http404()
    document = get_object_or_404(Document, pk=pk)
    uploaded = getattr(document, field)
    if not uploaded:
        raise Http404()
    try:
        return FileResponse(uploaded.open('rb'), as_attachment=True, filename=os.path.basename(uploaded.name))
    except (FileNotFoundError, OSError):
        raise Http404()
