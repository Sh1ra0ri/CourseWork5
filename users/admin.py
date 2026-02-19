from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Telegram", {"fields": ("telegram_chat_id",)}),)
    list_display = ("email", "username", "telegram_chat_id", "is_staff")
