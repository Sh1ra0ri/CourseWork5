from rest_framework.exceptions import ValidationError


def validate_reward_and_related(reward, related_habit):
    if reward and related_habit:
        raise ValidationError(
            "Нельзя одновременно указывать вознаграждение и связанную привычку."
        )


def validate_duration(duration):
    if duration and duration > 120:
        raise ValidationError("Время выполнения не может превышать 120 секунд.")


def validate_related_is_pleasant(related_habit):
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError("Связанная привычка должна быть приятной.")


def validate_pleasant_has_no_reward_or_related(is_pleasant, reward, related_habit):
    if is_pleasant:
        if reward:
            raise ValidationError("У приятной привычки не может быть вознаграждения.")
        if related_habit:
            raise ValidationError(
                "У приятной привычки не может быть связанной привычки."
            )


def validate_period(period):
    if period is not None:
        if period < 1 or period > 7:
            raise ValidationError("Периодичность должна быть от 1 до 7 дней.")
