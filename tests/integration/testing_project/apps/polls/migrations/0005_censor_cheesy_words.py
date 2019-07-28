# Generated by Django 2.2 on 2019-07-14 11:39
import re

from django.db import (
    migrations,
    models,
)

CHEESY_REGEXP = re.compile(r'chees\w*', re.IGNORECASE)


def censore_cheesy_words(apps, schema_editor):
    Question = apps.get_model('polls', 'Question')
    Choice = apps.get_model('polls', 'Choice')
    _censore_all_cheesy_words(Question, 'question_text')
    _censore_all_cheesy_words(Choice, 'choice_text')


def _censore_all_cheesy_words(model_class, text_field):
    # imagine this replace names of all kind of cheeses with sequence of `*`
    cheesy_instances = (
        model_class.objects.select_for_update()
        .filter(**{'{}__icontains'.format(text_field): 'chees'})
    )
    for instance in cheesy_instances:
        setattr(
            instance,
            text_field,
            CHEESY_REGEXP.sub(
                _censore_cheesy_word,
                getattr(instance, text_field),
            )
        )
        instance.save(update_fields=[text_field])
    gjetost_related_texts = model_class.objects.filter(
        **{'{}__icontains'.format(text_field): 'gjetost'}
    )
    if gjetost_related_texts.exists():
        raise ValueError(
            'Is `Gjetost` a real cheese? Review `Gjetost` related texts '
            'manually before running migration.'
        )


def _censore_cheesy_word(matchobj):
    return '*' * (matchobj.end() - matchobj.start())


class Migration(migrations.Migration):
    dependencies = [
        ('polls', '0004_populate_question_difficulty_level_field'),
    ]
    operations = [
        migrations.RunPython(
            code=censore_cheesy_words,
            reverse_code=migrations.RunPython.noop,
        )
    ]