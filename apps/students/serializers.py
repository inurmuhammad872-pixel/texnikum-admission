from rest_framework import serializers
from .models import Student, Direction, Document

class DirectionSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    available_quota = serializers.SerializerMethodField()

    class Meta:
        model = Direction
        fields = ['id', 'name', 'quota', 'available_quota', 'student_count', 'is_active', 'created_at']
        read_only_fields = ['created_at']

    def get_student_count(self, obj):
        return obj.students.filter(status='approved').count()

    def get_available_quota(self, obj):
        approved_count = obj.students.filter(status='approved').count()
        return obj.quota - approved_count


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'passport', 'attestat', 'photo', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class StudentListSerializer(serializers.ModelSerializer):
    direction_name = serializers.CharField(source='direction.name', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'fio', 'jshshir', 'phone', 'direction_name', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentDetailSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)
    direction = DirectionSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'fio', 'jshshir', 'phone', 'email', 'birth_date',
            'address', 'direction', 'status', 'rejection_reason',
            'document', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['fio', 'jshshir', 'phone', 'email', 'birth_date', 'address', 'direction']

    def validate_jshshir(self, value):
        if Student.objects.filter(jshshir=value).exists():
            raise serializers.ValidationError("Bu JSHSHIR allaqachon ro'yxatdan o'tgan!")
        return value

    def create(self, validated_data):
        student = Student.objects.create(**validated_data)
        Document.objects.create(student=student)
        return student