from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.forms.models import Category, Process, Form
from django.test import override_settings

from django.core.cache import cache

User = get_user_model()



@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class ReportViewTest(APITestCase):

    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@test.com",
            password="testpassword",
        )

        self.category = Category.objects.create(
            name="Test Category"
        )

        self.process = Process.objects.create(
            user=self.user,
            visibility="public",
            type="free",
            category=self.category,
        )

        self.form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

    def test_user_report_requires_authentication(self):
        url = reverse(
            "user-form-report",
            kwargs={"pk": self.form.id},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_user_report_authenticated(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "user-form-report",
            kwargs={"pk": self.form.id},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_process_report_requires_authentication(self):
        url = reverse(
            "process-report",
            kwargs={"pk": self.process.id},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_process_report_authenticated(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "process-report",
            kwargs={"pk": self.process.id},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_period_report_requires_admin(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("period_report")

        response = self.client.get(
            url,
            {"period": "weekly"},
        )

        self.assertEqual(response.status_code, 403)

    def test_period_report_invalid_period(self):
        admin = User.objects.create_superuser(
        username="admin",
        email="admin@test.com",
        password="adminpassword",
    )

        self.client.force_authenticate(user=admin)

        url = reverse("period_report")

        response = self.client.get(
            url,
            {"period": "yearly"},
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.data["detail"],
            "Invalid period. Allowed values are: weekly, monthly.",
        )