from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from .models import Student, Direction, Document
from .permissions import StudentStaffPermission, DirectionStaffPermission
from .serializers import (
    StudentListSerializer, StudentDetailSerializer, StudentCreateSerializer,
    DirectionSerializer, DocumentSerializer,
)


class DirectionViewSet(viewsets.ModelViewSet):
    serializer_class = DirectionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        qs = Direction.objects.annotate(approved_students_count=Count('students', filter=Q(students__status='approved')))
        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs

    def get_permissions(self):
        return [AllowAny()] if self.action in ('list', 'retrieve') else [DirectionStaffPermission()]


class StudentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'head', 'options']
    queryset = Student.objects.select_related('direction', 'document').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'direction']
    search_fields = ['fio', 'jshshir', 'phone']
    ordering_fields = ['created_at', 'fio']
    ordering = ['-created_at']

    def get_permissions(self):
        return [AllowAny()] if self.action == 'create' else [StudentStaffPermission()]

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        if self.action == 'create':
            return StudentCreateSerializer
        return StudentDetailSerializer

    def create(self, request, *args, **kwargs):
        if not settings.ADMISSIONS_OPEN:
            return Response({'error': 'Qabul hozircha ochilmagan.'}, status=503)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            student = serializer.save()
        except IntegrityError:
            return Response({'error': 'Ushbu JSHSHIR bo\'yicha ariza mavjud.'}, status=status.HTTP_409_CONFLICT)
        return Response(
            {'application_id': str(student.pk), 'message': 'Arizangiz qabul qilindi.'},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        with transaction.atomic():
            student = get_object_or_404(Student.objects.select_for_update(), pk=pk)
            direction = Direction.objects.select_for_update().get(pk=student.direction_id)
            if student.status not in ('pending', 'under_review'):
                return Response({'error': 'Ariza ushbu holatda tasdiqlanmaydi.'}, status=400)
            count = direction.students.filter(status='approved').count()
            student.status = 'approved' if count < direction.quota else 'waitlist'
            student.save(update_fields=['status', 'updated_at'])
        return Response({'status': student.status})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        reason = str(request.data.get('reason', '')).strip()
        if not reason or len(reason) > 2000:
            return Response({'error': 'Sababni (1-2000 ta belgi) kiriting.'}, status=400)
        with transaction.atomic():
            student = get_object_or_404(Student.objects.select_for_update(), pk=pk)
            if student.status == 'approved':
                return Response({'error': 'Tasdiqlangan arizani bu yerda rad etib bo\'lmaydi.'}, status=400)
            student.status = 'rejected'
            student.rejection_reason = reason
            student.save(update_fields=['status', 'rejection_reason', 'updated_at'])
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['get', 'post'])
    def documents(self, request, pk=None):
        student = self.get_object()
        document, _ = Document.objects.get_or_create(student=student)
        if request.method == 'GET':
            return Response(DocumentSerializer(document).data)
        serializer = DocumentSerializer(document, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        counts = {s: Student.objects.filter(status=s).count() for s in ('approved', 'pending', 'rejected')}
        total = Student.objects.count()
        return Response({
            'total_students': total,
            **counts,
            'conversion_rate': round(counts['approved'] * 100 / total, 2) if total else 0,
        })
