from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.forms.models import Category


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class CategoryViewSetTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # User 1
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # User 2
        self.other_user = CustomUser.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )

        # Authenticate as user 1
        self.client.force_authenticate(user=self.user)

        # Category belongs to user 1
        self.category = Category.objects.create(
            name="Test Category",
            user=self.user,
        )

        # Category belongs to user 2
        self.other_category = Category.objects.create(
            name="Other Category",
            user=self.other_user,
        )

    # ---------------------------------------------------------
    # LIST
    # ---------------------------------------------------------

    def test_list_categories_returns_only_current_user_categories(self):
        response = self.client.get(
            reverse("category-list")
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        # User 1 can see own category
        self.assertIn(
            self.category.id,
            returned_ids,
        )

        # User 1 cannot see user 2 category
        self.assertNotIn(
            self.other_category.id,
            returned_ids,
        )

    # ---------------------------------------------------------
    # RETRIEVE
    # ---------------------------------------------------------

    def test_user_can_retrieve_own_category(self):
        response = self.client.get(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["id"],
            self.category.id,
        )

        self.assertEqual(
            response.data["name"],
            "Test Category",
        )

    def test_user_cannot_retrieve_other_users_category(self):
        response = self.client.get(
            reverse(
                "category-detail",
                kwargs={"pk": self.other_category.id},
            )
        )

        # Because get_queryset() only contains current user's categories
        self.assertEqual(response.status_code, 404)

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def test_create_category(self):
        response = self.client.post(
            reverse("category-list"),
            {
                "name": "New Category",
            },
        )

        self.assertEqual(response.status_code, 201)

        category = Category.objects.get(
            name="New Category"
        )

        self.assertEqual(
            category.user,
            self.user,
        )

    # ---------------------------------------------------------
    # CREATE - USER CANNOT SET ANOTHER USER
    # ---------------------------------------------------------

    def test_create_category_belongs_to_authenticated_user(self):
        response = self.client.post(
            reverse("category-list"),
            {
                "name": "My Category",
                "user": self.other_user.id,
            },
        )

        self.assertEqual(response.status_code, 201)

        category = Category.objects.get(
            name="My Category"
        )

        # Even if client sends another user's ID,
        # perform_create() must use request.user.
        self.assertEqual(
            category.user,
            self.user,
        )

        self.assertNotEqual(
            category.user,
            self.other_user,
        )

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def test_user_can_update_own_category(self):
        response = self.client.patch(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            ),
            {
                "name": "Updated Category",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.category.refresh_from_db()

        self.assertEqual(
            self.category.name,
            "Updated Category",
        )

        self.assertEqual(
            self.category.user,
            self.user,
        )

    def test_user_cannot_update_other_users_category(self):
        response = self.client.patch(
            reverse(
                "category-detail",
                kwargs={"pk": self.other_category.id},
            ),
            {
                "name": "Hacked Category",
            },
        )

        self.assertEqual(response.status_code, 404)

        self.other_category.refresh_from_db()

        self.assertEqual(
            self.other_category.name,
            "Other Category",
        )

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def test_user_can_delete_own_category(self):
        response = self.client.delete(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            )
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Category.objects.filter(
                id=self.category.id
            ).exists()
        )

    def test_user_cannot_delete_other_users_category(self):
        response = self.client.delete(
            reverse(
                "category-detail",
                kwargs={"pk": self.other_category.id},
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Category.objects.filter(
                id=self.other_category.id
            ).exists()
        )

    # ---------------------------------------------------------
    # AUTHENTICATION
    # ---------------------------------------------------------

    def test_unauthenticated_user_cannot_list_categories(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("category-list")
        )

        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_create_category(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            reverse("category-list"),
            {
                "name": "Unauthenticated Category",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_retrieve_category(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            )
        )

        self.assertEqual(response.status_code, 401)