from django.db import models
import uuid

class Direction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True, db_index=True)
    quota = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Direction"
        verbose_name_plural = "Directions"

    def __str__(self):
        return self.name


class Student(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('need_clarification', 'Need Clarification'),
        ('waitlist', 'Waitlist'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fio = models.CharField(max_length=200, db_index=True)
    jshshir = models.CharField(max_length=14, unique=True, db_index=True)
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField()
    birth_date = models.DateField()
    address = models.TextField()
    direction = models.ForeignKey(Direction, on_delete=models.PROTECT, related_name='students')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.fio} ({self.jshshir})"


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='document')
    passport = models.FileField(upload_to='students/%Y/%m/%d/', null=True, blank=True)
    attestat = models.FileField(upload_to='students/%Y/%m/%d/', null=True, blank=True)
    photo = models.ImageField(upload_to='students/%Y/%m/%d/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"Documents for {self.student.fio}"