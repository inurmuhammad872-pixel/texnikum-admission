from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Student, Direction, Document


class AdmissionsTests(TestCase):
    def setUp(self):
        self.direction = Direction.objects.create(name='Test direction', quota=1)
        self.client_api = APIClient()
        self.valid_data = {
            'fio': 'Test Applicant',
            'jshshir': '12345678901234',
            'phone': '+998901234567',
            'email': 'applicant@example.com',
            'birth_date': '2007-01-01',
            'address': 'Test address',
            'direction': str(self.direction.pk),
            'consent': True,
        }

    def test_mobile_viewport_meta_and_form_render(self):
        response = self.client.get(reverse('apply'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'width=device-width')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="consent"')

    def test_public_direction_read_only(self):
        self.assertEqual(self.client_api.get('/api/v1/directions/').status_code, 200)
        self.assertEqual(self.client_api.post('/api/v1/directions/', {'name': 'Intruder', 'quota': 1}).status_code, 403)

    def test_student_list_and_approval_are_private(self):
        self.assertEqual(self.client_api.get('/api/v1/students/').status_code, 403)
        self.assertEqual(self.client_api.get('/api/v1/students/statistics/').status_code, 403)
        self.assertEqual(self.client_api.post('/api/v1/students/00000000-0000-0000-0000-000000000001/approve/').status_code, 403)

    def test_public_application_api_records_consent(self):
        response = self.client_api.post('/api/v1/students/', self.valid_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('jshshir', response.data)
        student = Student.objects.get()
        self.assertIsNotNone(student.consent_at)
        self.assertTrue(Document.objects.filter(student=student).exists())

    def test_invalid_jshshir_and_missing_consent(self):
        data = {**self.valid_data, 'jshshir': '1234', 'consent': False}
        response = self.client_api.post('/api/v1/students/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Student.objects.count(), 0)

    def test_web_form_saves_then_redirects(self):
        payload = {**self.valid_data, 'consent': 'on'}
        response = self.client.post(reverse('apply'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Student.objects.count(), 1)
        result = self.client.get(response['Location'])
        self.assertContains(result, 'Arizangiz qabul qilindi')

    def test_staff_quota_enforced(self):
        user = get_user_model().objects.create_superuser('admin', 'admin@example.com', 'test-only-password')
        self.client_api.force_authenticate(user=user)
        for i in range(2):
            data = {**self.valid_data, 'jshshir': f'1234567890123{i}'}
            # Authenticate as staff for this test's creation; create is public also.
            resp = self.client_api.post('/api/v1/students/', data, format='json')
            self.assertEqual(resp.status_code, 201)
        students = list(Student.objects.order_by('created_at'))
        first = self.client_api.post(f'/api/v1/students/{students[0].pk}/approve/')
        second = self.client_api.post(f'/api/v1/students/{students[1].pk}/approve/')
        self.assertEqual(first.data['status'], 'approved')
        self.assertEqual(second.data['status'], 'waitlist')

    @override_settings(ADMISSIONS_OPEN=False)
    def test_public_submissions_closed_in_production_until_explicitly_enabled(self):
        response = self.client_api.post('/api/v1/students/', self.valid_data, format='json')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(Student.objects.count(), 0)
        response = self.client.post(reverse('apply'), {**self.valid_data, 'consent': 'on'})
        self.assertEqual(response.status_code, 503)
        response = self.client.get(reverse('apply'))
        self.assertContains(response, 'Qabul hozircha ochilmagan')

    def test_anonymous_document_download_is_denied(self):
        student = Student.objects.create(
            fio='Test', jshshir='11111111111111', phone='+998901234567',
            email='test@example.com', birth_date=date(2006, 1, 1),
            address='Test', direction=self.direction,
        )
        document = Document.objects.create(student=student)
        response = self.client.get(reverse('private_document', args=(document.pk, 'passport')))
        self.assertIn(response.status_code, (302, 403))
