from celery import shared_task
from django.utils import timezone

from habits.services import send_telegram_message


@shared_task
def send_habit_reminders():
    from habits.models import Habit

    now = timezone.now()
    current_time = now.time().replace(second=0, microsecond=0)
    current_weekday = now.weekday()

    habits = (
        Habit.objects.filter(
            is_pleasant=False,
            user__telegram_chat_id__isnull=False,
        )
        .exclude(
            user__telegram_chat_id="",
        )
        .select_related("user")
    )

    for habit in habits:
        habit_time = habit.time.replace(second=0, microsecond=0)

        if habit_time != current_time:
            continue
        if habit.period == 1 or (current_weekday % habit.period == 0):
            message = (
                f"Привет! Напоминаю о твоей привычке:\n\n"
                f"Я буду {habit.action} "
                f'в {habit.time.strftime("%H:%M")} '
                f"в {habit.place}.\n\n"
                f"Время на выполнение: {habit.duration} сек."
            )
            if habit.reward:
                message += f"\nВознаграждение: {habit.reward}"

            send_telegram_message(habit.user.telegram_chat_id, message)
