from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegisterTestCase(APITestCase):

    def setUp(self):
        self.url = reverse("register")
        self.valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpass123",
        }

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "test@example.com")

    def test_register_duplicate_email(self):
        self.client.post(self.url, self.valid_data)
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        data = self.valid_data.copy()
        data["email"] = "not-an-email"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password(self):
        data = self.valid_data.copy()
        data["password"] = "123"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_hashed(self):
        self.client.post(self.url, self.valid_data)
        user = User.objects.get(email="test@example.com")
        self.assertTrue(user.check_password("strongpass123"))


class JWTAuthTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="testpass123",
        )
        self.token_url = reverse("token_obtain_pair")

    def test_obtain_token_success(self):
        response = self.client.post(
            self.token_url,
            {
                "email": "auth@example.com",
                "password": "testpass123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_wrong_password(self):
        response = self.client.post(
            self.token_url,
            {
                "email": "auth@example.com",
                "password": "wrongpass",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
