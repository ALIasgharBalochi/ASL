import uuid

from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationViewTests(APITestCase):

    def setUp(self):
        self.redis = get_redis_connection("default")

        self.redis.flushdb()

        self.url = "/accounts/api/registration/"

        self.data = {
            "username": "ali",
            "first_name": "Ali",
            "last_name": "Balochi",
            "email": "ali@example.com",
            "password": "StrongPassword123",
        }

    def tearDown(self):
        self.redis.flushdb()

    def test_registration_success(self):
        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("regestratoin_id", response.data)

        registration_id = response.data["regestratoin_id"]

        registration_key = f"registration:{registration_id}"

        data = self.redis.hgetall(registration_key)

        self.assertTrue(data)

        self.assertEqual(data[b"username"], b"ali")
        self.assertEqual(data[b"email"], b"ali@example.com")

        self.assertNotEqual(
            data[b"password"].decode(),
            self.data["password"],
        )

        otp_key = f"registration:{registration_id}:otp"

        otp_data = self.redis.hgetall(otp_key)

        self.assertTrue(otp_data)
        self.assertIn(b"otp", otp_data)

    def test_registration_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email=self.data["email"],
            password="password123",
        )

        response = self.client.post(
            self.url,
            self.data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(self.redis.keys("registration:*"))


class VerifyOtpViewTests(APITestCase):

    def setUp(self):
        self.redis = get_redis_connection("default")
        self.redis.flushdb()

        self.registration_url = "/accounts/api/registration/"
        self.verify_url = "/accounts/api/verify_otp/"

        self.data = {
            "username": "ali",
            "first_name": "Ali",
            "last_name": "Balochi",
            "email": "ali@example.com",
            "password": "StrongPassword123",
        }

    def tearDown(self):
        self.redis.flushdb()

    def create_registration(self):
        response = self.client.post(
            self.registration_url,
            self.data,
            format="json",
        )

        registration_id = response.data["regestratoin_id"]

        otp_key = f"registration:{registration_id}:otp"
        otp = self.redis.hget(otp_key, "otp").decode()

        return registration_id, otp

    def test_verify_otp_success_creates_user(self):
        registration_id, otp = self.create_registration()

        response = self.client.post(
            self.verify_url,
            {
                "registration_id": registration_id,
                "otp": otp,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(User.objects.filter(email=self.data["email"]).exists())

        self.assertFalse(self.redis.exists(f"registration:{registration_id}"))

        self.assertFalse(self.redis.exists(f"registration:{registration_id}:otp"))

    def test_verify_with_wrong_otp_fails(self):
        registration_id, otp = self.create_registration()

        wrong_otp = "000000"

        if wrong_otp == otp:
            wrong_otp = "111111"

        response = self.client.post(
            self.verify_url,
            {
                "registration_id": registration_id,
                "otp": wrong_otp,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(User.objects.filter(email=self.data["email"]).exists())

    def test_verify_with_nonexistent_registration_fails(self):
        registration_id = uuid.uuid4()

        response = self.client.post(
            self.verify_url,
            {
                "registration_id": str(registration_id),
                "otp": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(User.objects.filter(email=self.data["email"]).exists())

    def test_otp_cannot_be_used_twice(self):
        registration_id, otp = self.create_registration()

        first_response = self.client.post(
            self.verify_url,
            {
                "registration_id": registration_id,
                "otp": otp,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        second_response = self.client.post(
            self.verify_url,
            {
                "registration_id": registration_id,
                "otp": otp,
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            User.objects.filter(email=self.data["email"]).count(),
            1,
        )


class RegenerateOtpViewTests(APITestCase):

    def setUp(self):
        self.redis = get_redis_connection("default")
        self.redis.flushdb()

        self.registration_url = "/accounts/api/registration/"
        self.regenerate_url = "/accounts/api/regenerate_otp/"

        self.data = {
            "username": "ali",
            "first_name": "Ali",
            "last_name": "Balochi",
            "email": "ali@example.com",
            "password": "StrongPassword123",
        }

    def tearDown(self):
        self.redis.flushdb()

    def create_registration(self):
        response = self.client.post(
            self.registration_url,
            self.data,
            format="json",
        )

        registration_id = response.data["regestratoin_id"]

        otp_key = f"registration:{registration_id}:otp"

        old_otp = self.redis.hget(
            otp_key,
            "otp",
        ).decode()

        return registration_id, old_otp

    def test_regenerate_otp_success(self):
        registration_id, old_otp = self.create_registration()

        response = self.client.post(
            self.regenerate_url,
            {
                "registration_id": registration_id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["regestratoin_id"],
            registration_id,
        )

        otp_key = f"registration:{registration_id}:otp"

        new_otp = self.redis.hget(
            otp_key,
            "otp",
        ).decode()

        self.assertTrue(new_otp)

        self.assertNotEqual(
            old_otp,
            new_otp,
        )

    def test_old_otp_is_invalid_after_regeneration(self):
        registration_id, old_otp = self.create_registration()

        response = self.client.post(
            self.regenerate_url,
            {
                "registration_id": registration_id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        verify_response = self.client.post(
            "/accounts/api/verify_otp/",
            {
                "registration_id": registration_id,
                "otp": old_otp,
            },
            format="json",
        )

        self.assertEqual(
            verify_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(User.objects.filter(email=self.data["email"]).exists())

    def test_regenerated_otp_can_verify_registration(self):
        registration_id, old_otp = self.create_registration()

        self.client.post(
            self.regenerate_url,
            {
                "registration_id": registration_id,
            },
            format="json",
        )

        otp_key = f"registration:{registration_id}:otp"

        new_otp = self.redis.hget(
            otp_key,
            "otp",
        ).decode()

        response = self.client.post(
            "/accounts/api/verify_otp/",
            {
                "registration_id": registration_id,
                "otp": new_otp,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(User.objects.filter(email=self.data["email"]).exists())
