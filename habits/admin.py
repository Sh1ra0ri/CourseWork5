from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "user",
        "place",
        "time",
        "is_pleasant",
        "is_public",
        "period",
        "duration",
    )
    list_filter = ("is_pleasant", "is_public")
    search_fields = ("action", "place", "user__email")
    readonly_fields = ("created_at",)
