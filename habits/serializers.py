from rest_framework import serializers

from habits.models import Habit
from habits.validators import (
    validate_duration,
    validate_period,
    validate_pleasant_has_no_reward_or_related,
    validate_related_is_pleasant,
    validate_reward_and_related,
)


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "period",
            "reward",
            "duration",
            "is_public",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def validate(self, data):
        reward = data.get("reward")
        related_habit = data.get("related_habit")
        duration = data.get("duration")
        period = data.get("period")
        is_pleasant = data.get("is_pleasant", False)

        validate_reward_and_related(reward, related_habit)
        validate_duration(duration)
        validate_related_is_pleasant(related_habit)
        validate_pleasant_has_no_reward_or_related(is_pleasant, reward, related_habit)
        validate_period(period)

        return data


class HabitPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = (
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "period",
            "reward",
            "duration",
        )
