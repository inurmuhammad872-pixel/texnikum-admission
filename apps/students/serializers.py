import re
from datetime import date
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import Student, Direction, Document


class DirectionSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    available_quota = serializers.SerializerMethodField()

    class Meta:
        model = Direction
        fields = ['id', 'name', 'quota', 'student_count', 'available_quota', 'is_active']
        read_only_fields = ['id', 'student_count', 'available_quota']

    def get_student_count(self, obj):
        return getattr(obj, 'approved_students_count', None) if hasattr(obj, 'approved_students_count') else obj.students.filter(status='approved').count()

    def get_available_quota(self, obj):
        return max(0, obj.quota - self.get_student_count(obj))


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'passport', 'attestat', 'photo', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class StudentListSerializer(serializers.ModelSerializer):
    direction_name = serializers.CharField(source='direction.name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'fio', 'jshshir', 'phone', 'direction_name', 'status', 'created_at']


class StudentDetailSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)
    direction = DirectionSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'fio', 'jshshir', 'phone', 'email', 'birth_date', 'address',
            'direction', 'status', 'rejection_reason', 'document', 'created_at', 'updated_at',
            'consent_at', 'consent_version',
        ]
        read_only_fields = fields


class StudentCreateSerializer(serializers.ModelSerializer):
    consent = serializers.BooleanField(write_only=True)

    class Meta:
        model = Student
        fields = ['fio', 'jshshir', 'phone', 'email', 'birth_date', 'address', 'direction', 'consent']

    def validate_consent(self, value):
        if value is not True:
            raise serializers.ValidationError('Shaxsiy ma\'lumotlarni qayta ishlashga rozilik majburiy.')
        return value

    def validate_jshshir(self, value):
        if not re.fullmatch(r'\d{14}', value):
            raise serializers.ValidationError('JSHSHIR 14 ta raqamdan iborat bo\'lishi kerak.')
        if Student.objects.filter(jshshir=value).exists():
            raise serializers.ValidationError('Bu JSHSHIR bilan ariza mavjud.')
        return value

    def validate_birth_date(self, value):
        if value >= date.today() or value.year < 1900:
            raise serializers.ValidationError('Tug\'ilgan sanani tekshiring.')
        return value

    def validate_direction(self, value):
        if not value.is_active:
            raise serializers.ValidationError('Ushbu yo\'nalishga qabul yopilgan.')
        return value

    def validate_phone(self, value):
        digits = re.sub(r'\D', '', value)
        if len(digits) == 9:
            digits = '998' + digits
        if len(digits) != 12 or not digits.startswith('998'):
            raise serializers.ValidationError('Telefon: +998 XX XXX XX XX formatida kiriting.')
        return '+' + digits

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('consent')
        student = Student.objects.create(consent_at=timezone.now(), consent_version='v1', **validated_data)
        Document.objects.create(student=student)
        return student
