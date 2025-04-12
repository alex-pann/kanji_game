from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Kanji(models.Model):
    image = models.ImageField(upload_to='kanji_images/')
    correct_translation = models.CharField(max_length=100)
    wrong_option1 = models.CharField(max_length=100)
    wrong_option2 = models.CharField(max_length=100)

    def __str__(self):
        return self.correct_translation

class Score(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)