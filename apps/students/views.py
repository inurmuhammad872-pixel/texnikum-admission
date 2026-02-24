from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Student, Direction, Document
from .serializers import (
    StudentListSerializer, StudentDetailSerializer, StudentCreateSerializer,
    DirectionSerializer, DocumentSerializer
)

class DirectionViewSet(viewsets.ModelViewSet):
    queryset = Direction.objects.filter(is_active=True)
    serializer_class = DirectionSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('direction', 'document').all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'direction']
    search_fields = ['fio', 'jshshir', 'phone']
    ordering_fields = ['created_at', 'fio']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        elif self.action == 'create':
            return StudentCreateSerializer
        return StudentDetailSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        student = self.get_object()
        
        if student.status not in ['pending', 'under_review']:
            return Response(
                {'error': 'Faqat pending yoki under_review studentlarni qabul qilish mumkin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Kvota tekshirish
        direction = student.direction
        approved_count = direction.students.filter(status='approved').count()
        
        if approved_count >= direction.quota:
            student.status = 'waitlist'
            student.save()
            return Response({'message': 'Kvota tugadi, waitlist-ga qo\'shildi'}, status=status.HTTP_200_OK)
        
        student.status = 'approved'
        student.save()
        return Response({'message': 'Student qabul qilindi'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        student = self.get_object()
        reason = request.data.get('reason', '')
        student.status = 'rejected'
        student.rejection_reason = reason
        student.save()
        return Response({'message': 'Student rad etildi'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'])
    def documents(self, request, pk=None):
        student = self.get_object()
        
        if request.method == 'GET':
            try:
                document = student.document
                serializer = DocumentSerializer(document)
                return Response(serializer.data)
            except Document.DoesNotExist:
                return Response({'error': 'Hujjat topilmadi'}, status=status.HTTP_404_NOT_FOUND)
        
        elif request.method == 'POST':
            try:
                document = student.document
                serializer = DocumentSerializer(document, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Document.DoesNotExist:
                return Response({'error': 'Hujjat topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total = Student.objects.count()
        approved = Student.objects.filter(status='approved').count()
        pending = Student.objects.filter(status='pending').count()
        rejected = Student.objects.filter(status='rejected').count()
        
        return Response({
            'total_students': total,
            'approved': approved,
            'pending': pending,
            'rejected': rejected,
            'conversion_rate': round((approved / total * 100), 2) if total > 0 else 0
        })