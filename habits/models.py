from django.conf import settings
from django.db import models

from habits.validators import (
    validate_duration,
    validate_period,
    validate_pleasant_has_no_reward_or_related,
    validate_related_is_pleasant,
    validate_reward_and_related,
)


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField(
        max_length=255,
        verbose_name="Место",
        help_text="Место где пользователь должен выполнять привычку",
    )
    time = models.TimeField(
        verbose_name="Время", help_text="Время когда человек должен выполнять привычку"
    )
    action = models.CharField(
        max_length=255,
        verbose_name="Действие",
        help_text="Действие которое представляет собой привычка",
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_to",
        verbose_name="Связанная привычка",
    )
    period = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Периодичность (дней)",
        help_text="Как часто выполнять привычку",
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
        help_text="Награда после выполнения привычки",
    )
    duration = models.PositiveSmallIntegerField(
        verbose_name="Время на выполнение (секунд)",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
        help_text="Публичные привычки которые видны всем пользователям",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} в {self.time} в {self.place}"

    def clean(self):
        validate_reward_and_related(self.reward, self.related_habit)
        validate_duration(self.duration)
        validate_related_is_pleasant(self.related_habit)
        validate_pleasant_has_no_reward_or_related(
            self.is_pleasant, self.reward, self.related_habit
        )
        validate_period(self.period)
