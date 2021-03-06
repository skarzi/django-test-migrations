# Generated by Django 2.2 on 2019-07-14 11:39
from django.db import (
    migrations,
    models,
)


def populate_difficulty_level(apps, schema_editor):
    Question = apps.get_model('polls', 'Question')
    Question.objects.select_for_update().update(
        difficulty_level=models.F('is_hard') + 2,
    )


def reverse_difficulty_level_to_is_hard(apps, schema_editor):
    Question = apps.get_model('polls', 'Question')
    Question.objects.select_for_update().update(
        is_hard=models.Case(
            models.When(difficulty_level__gt=2, then=True),
            default=False
        ),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('polls', '0003_question_difficulty_level'),
    ]
    operations = [
        migrations.RunPython(
            code=populate_difficulty_level,
            reverse_code=reverse_difficulty_level_to_is_hard,
        )
    ]
