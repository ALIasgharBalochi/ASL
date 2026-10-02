from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class ResetPasswordBaseTestCase(APITestCase):

    def setUp(self):
        self.redis = get_redis_connection("default")
        self.redis.flushdb()

        self.user = User.objects.create_user(
            username="ali",
            email="ali@example.com",
            password="OldPassword123",
        )

        self.reset_url = "/accounts/api/reset-password/"
        self.verify_url = "/accounts/api/reset-password/verify/"
        self.change_url = "/accounts/api/reset-password/change/"

        self.email = self.user.email

    def tearDown(self):
        self.redis.flushdb()


class ResetPasswordViewTests(ResetPasswordBaseTestCase):

    def test_request_reset_password_success(self):
        response = self.client.post(
            self.reset_url,
            {
                "email": self.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("finder_id", response.data)

        finder_id = response.data["finder_id"]

        finder_key = f"finder_id:{finder_id}"

        data = self.redis.hgetall(finder_key)

        self.assertTrue(data)
        self.assertEqual(
            data[b"email"],
            self.email.encode(),
        )

        otp_key = f"finder_id:{finder_id}:otp"

        otp_data = self.redis.hgetall(otp_key)

        self.assertTrue(otp_data)
        self.assertIn(b"otp", otp_data)

    def test_request_reset_password_for_nonexistent_user(self):
        response = self.client.post(
            self.reset_url,
            {
                "email": "doesnotexist@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(self.redis.keys("finder_id:*"))


class VerifyResetPasswordOTPViewTests(ResetPasswordBaseTestCase):

    def create_reset_request(self):
        response = self.client.post(
            self.reset_url,
            {
                "email": self.email,
            },
            format="json",
        )

        finder_id = response.data["finder_id"]

        otp_key = f"finder_id:{finder_id}:otp"

        otp = self.redis.hget(
            otp_key,
            "otp",
        ).decode()

        return finder_id, otp

    def test_verify_reset_otp_success(self):
        finder_id, otp = self.create_reset_request()

        response = self.client.post(
            self.verify_url,
            {
                "finder_id": finder_id,
                "otp": otp,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        verified_key = f"finder_id:{finder_id}:verified"

        self.assertTrue(self.redis.exists(verified_key))

        otp_key = f"finder_id:{finder_id}:otp"

        self.assertFalse(self.redis.exists(otp_key))

    def test_verify_reset_otp_with_wrong_otp(self):
        finder_id, otp = self.create_reset_request()

        wrong_otp = "000000"

        if wrong_otp == otp:
            wrong_otp = "111111"

        response = self.client.post(
            self.verify_url,
            {
                "finder_id": finder_id,
                "otp": wrong_otp,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        verified_key = f"finder_id:{finder_id}:verified"

        self.assertFalse(self.redis.exists(verified_key))

    def test_verify_reset_otp_with_invalid_finder_id(self):
        import uuid

        finder_id = uuid.uuid4()

        response = self.client.post(
            self.verify_url,
            {
                "finder_id": str(finder_id),
                "otp": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        verified_key = f"finder_id:{finder_id}:verified"

        self.assertFalse(self.redis.exists(verified_key))

    def test_reset_otp_cannot_be_used_twice(self):
        finder_id, otp = self.create_reset_request()

        first_response = self.client.post(
            self.verify_url,
            {
                "finder_id": finder_id,
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
                "finder_id": finder_id,
                "otp": otp,
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class ChangeResetPasswordViewTests(ResetPasswordBaseTestCase):

    def create_verified_reset(self):
        response = self.client.post(
            self.reset_url,
            {
                "email": self.email,
            },
            format="json",
        )

        finder_id = response.data["finder_id"]

        otp_key = f"finder_id:{finder_id}:otp"

        otp = self.redis.hget(
            otp_key,
            "otp",
        ).decode()

        verify_response = self.client.post(
            self.verify_url,
            {
                "finder_id": finder_id,
                "otp": otp,
            },
            format="json",
        )

        self.assertEqual(
            verify_response.status_code,
            status.HTTP_200_OK,
        )

        return finder_id

    def test_change_password_without_verification_fails(self):
        response = self.client.post(
            self.reset_url,
            {
                "email": self.email,
            },
            format="json",
        )

        finder_id = response.data["finder_id"]

        response = self.client.post(
            self.change_url,
            {
                "finder_id": finder_id,
                "new_password": "NewPassword123",
                "verify_password": "NewPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("OldPassword123"))

    def test_change_password_success(self):
        finder_id = self.create_verified_reset()

        response = self.client.post(
            self.change_url,
            {
                "finder_id": finder_id,
                "new_password": "NewPassword123",
                "verify_password": "NewPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("NewPassword123"))

        self.assertFalse(self.user.check_password("OldPassword123"))

        verified_key = f"finder_id:{finder_id}:verified"
        finder_key = f"finder_id:{finder_id}"

        self.assertFalse(self.redis.exists(verified_key))

        self.assertFalse(self.redis.exists(finder_key))

    def test_change_password_with_different_passwords_fails(self):
        finder_id = self.create_verified_reset()

        response = self.client.post(
            self.change_url,
            {
                "finder_id": finder_id,
                "new_password": "NewPassword123",
                "verify_password": "DifferentPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password("OldPassword123"))

    def test_change_password_with_invalid_finder_id_fails(self):
        import uuid

        finder_id = uuid.uuid4()

        response = self.client.post(
            self.change_url,
            {
                "finder_id": str(finder_id),
                "new_password": "NewPassword123",
                "verify_password": "NewPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
