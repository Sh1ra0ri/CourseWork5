from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from habits.models import Habit
from habits.validators import (
    validate_duration,
    validate_period,
    validate_pleasant_has_no_reward_or_related,
    validate_related_is_pleasant,
    validate_reward_and_related,
)

User = get_user_model()


class BaseHabitTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="habituser",
            email="habit@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )
        self._authenticate(self.user)

    def _authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def _create_habit(self, user=None, **kwargs):
        defaults = {
            "place": "Дом",
            "time": "08:00:00",
            "action": "Читать книгу",
            "duration": 60,
            "period": 1,
            "is_pleasant": False,
            "is_public": False,
        }
        defaults.update(kwargs)
        return Habit.objects.create(user=user or self.user, **defaults)


class ValidatorTestCase(BaseHabitTestCase):

    def test_reward_and_related_raises(self):
        pleasant = self._create_habit(is_pleasant=True)
        from rest_framework.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_reward_and_related("Кофе", pleasant)

    def test_reward_and_related_ok_only_reward(self):
        validate_reward_and_related("Кофе", None)

    def test_reward_and_related_ok_only_related(self):
        pleasant = self._create_habit(is_pleasant=True)
        validate_reward_and_related(None, pleasant)

    def test_duration_over_120_raises(self):
        from rest_framework.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_duration(121)

    def test_duration_120_ok(self):
        validate_duration(120)

    def test_related_not_pleasant_raises(self):
        from rest_framework.exceptions import ValidationError

        not_pleasant = self._create_habit(is_pleasant=False)
        with self.assertRaises(ValidationError):
            validate_related_is_pleasant(not_pleasant)

    def test_related_pleasant_ok(self):
        pleasant = self._create_habit(is_pleasant=True)
        validate_related_is_pleasant(pleasant)

    def test_pleasant_with_reward_raises(self):
        from rest_framework.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_pleasant_has_no_reward_or_related(True, "Кофе", None)

    def test_pleasant_with_related_raises(self):
        from rest_framework.exceptions import ValidationError

        pleasant = self._create_habit(is_pleasant=True)
        with self.assertRaises(ValidationError):
            validate_pleasant_has_no_reward_or_related(True, None, pleasant)

    def test_period_over_7_raises(self):
        from rest_framework.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_period(8)

    def test_period_zero_raises(self):
        from rest_framework.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_period(0)

    def test_period_7_ok(self):
        validate_period(7)

    def test_period_1_ok(self):
        validate_period(1)


class HabitModelTestCase(BaseHabitTestCase):

    def test_str(self):
        habit = self._create_habit()
        self.assertIn("Читать книгу", str(habit))

    def test_default_period(self):
        habit = self._create_habit()
        self.assertEqual(habit.period, 1)

    def test_default_is_pleasant(self):
        habit = self._create_habit()
        self.assertFalse(habit.is_pleasant)

    def test_default_is_public(self):
        habit = self._create_habit()
        self.assertFalse(habit.is_public)


class HabitListTestCase(BaseHabitTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("habit-list")

    def test_list_only_own_habits(self):
        self._create_habit()
        self._create_habit(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_requires_auth(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination_page_size(self):
        for _ in range(6):
            self._create_habit()
        response = self.client.get(self.url)
        self.assertEqual(len(response.data["results"]), 5)

    def test_pagination_second_page(self):
        for _ in range(6):
            self._create_habit()
        response = self.client.get(self.url + "?page=2")
        self.assertEqual(len(response.data["results"]), 1)


class HabitPublicListTestCase(BaseHabitTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("habit-public-list")

    def test_public_list_shows_only_public(self):
        self._create_habit(is_public=True)
        self._create_habit(is_public=False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_public_list_shows_other_users_habits(self):
        self._create_habit(user=self.other_user, is_public=True)
        response = self.client.get(self.url)
        self.assertEqual(response.data["count"], 1)

    def test_public_list_requires_auth(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HabitCreateTestCase(BaseHabitTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("habit-create")
        self.valid_data = {
            "place": "Парк",
            "time": "07:00:00",
            "action": "Бегать",
            "duration": 90,
            "period": 1,
            "is_pleasant": False,
            "is_public": False,
        }

    def test_create_success(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        self.assertEqual(Habit.objects.get().user, self.user)

    def test_create_requires_auth(self):
        self.client.credentials()
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_with_reward_and_related_fails(self):
        pleasant = self._create_habit(is_pleasant=True)
        data = self.valid_data.copy()
        data["reward"] = "Кофе"
        data["related_habit"] = pleasant.pk
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duration_over_120_fails(self):
        data = self.valid_data.copy()
        data["duration"] = 121
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_period_over_7_fails(self):
        data = self.valid_data.copy()
        data["period"] = 8
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pleasant_with_reward_fails(self):
        data = self.valid_data.copy()
        data["is_pleasant"] = True
        data["reward"] = "Кофе"
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_related_not_pleasant_fails(self):
        not_pleasant = self._create_habit(is_pleasant=False)
        data = self.valid_data.copy()
        data["related_habit"] = not_pleasant.pk
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_pleasant_related_success(self):
        pleasant = self._create_habit(is_pleasant=True)
        data = self.valid_data.copy()
        data["related_habit"] = pleasant.pk
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class HabitUpdateTestCase(BaseHabitTestCase):

    def setUp(self):
        super().setUp()
        self.habit = self._create_habit()
        self.url = reverse("habit-update", args=[self.habit.pk])

    def test_update_own_habit(self):
        response = self.client.patch(self.url, {"action": "Медитировать"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.action, "Медитировать")

    def test_update_other_user_habit_forbidden(self):
        other_habit = self._create_habit(user=self.other_user)
        url = reverse("habit-update", args=[other_habit.pk])
        response = self.client.patch(url, {"action": "Медитировать"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_requires_auth(self):
        self.client.credentials()
        response = self.client.patch(self.url, {"action": "Медитировать"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HabitDestroyTestCase(BaseHabitTestCase):

    def setUp(self):
        super().setUp()
        self.habit = self._create_habit()
        self.url = reverse("habit-delete", args=[self.habit.pk])

    def test_delete_own_habit(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)

    def test_delete_other_user_habit_forbidden(self):
        other_habit = self._create_habit(user=self.other_user)
        url = reverse("habit-delete", args=[other_habit.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_requires_auth(self):
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
