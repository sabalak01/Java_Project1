from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Deck(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Flashcard(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='flashcards')
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_reviewed = models.DateTimeField(default=timezone.now)
    repetition_interval = models.IntegerField(default=1)  # Интервал в днях

    def __str__(self):
        return self.question


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    last_reviewed = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0)

