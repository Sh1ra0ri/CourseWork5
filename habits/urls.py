from django.urls import path

from habits.views import (
    HabitCreateView,
    HabitDestroyView,
    HabitListView,
    HabitPublicListView,
    HabitUpdateView,
)

urlpatterns = [
    path("", HabitListView.as_view(), name="habit-list"),
    path("public/", HabitPublicListView.as_view(), name="habit-public-list"),
    path("create/", HabitCreateView.as_view(), name="habit-create"),
    path("<int:pk>/update/", HabitUpdateView.as_view(), name="habit-update"),
    path("<int:pk>/delete/", HabitDestroyView.as_view(), name="habit-delete"),
]
