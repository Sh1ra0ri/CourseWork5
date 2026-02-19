from rest_framework import generics, permissions

from habits.models import Habit
from habits.permissions import IsOwner
from habits.serializers import HabitPublicSerializer, HabitSerializer


class HabitListView(generics.ListAPIView):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()
        return Habit.objects.filter(user=self.request.user)


class HabitPublicListView(generics.ListAPIView):
    serializer_class = HabitPublicSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Habit.objects.filter(is_public=True)


class HabitCreateView(generics.CreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]


class HabitUpdateView(generics.UpdateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()
        return Habit.objects.filter(user=self.request.user)


class HabitDestroyView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()
        return Habit.objects.filter(user=self.request.user)
