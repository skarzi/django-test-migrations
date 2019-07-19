from django.db import models

from . import enums


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    is_hard = models.BooleanField(default=False)
    difficulty_level = models.PositiveSmallIntegerField(
        choices=enums.DifficultyLevel.choices(),
        default=enums.DifficultyLevel.MEDIUM.value,
    )

    def __str__(self) -> str:
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(
        'polls.Question',
        on_delete=models.CASCADE,
        related_name='choices',
    )
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.choice_text} [{self.votes}]'
