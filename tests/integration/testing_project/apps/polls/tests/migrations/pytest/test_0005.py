import datetime

import pytest

from apps.polls import enums
from django.db.migrations.exceptions import IrreversibleError
from django.test import tag


@tag('pytest')
class TestMigration0005:
    migrate_from = [('polls', '0004_populate_question_difficulty_level_field')]
    migrate_to = [('polls', '0005_censor_cheesy_words')]

    def test_cheesy_words_are_censored_in_Question_and_Choice_instances(
            self,
            migrator,
    ):
        old_apps = migrator.migrate_from(self.migrate_from)
        Question = old_apps.get_model('polls', 'Question')
        Choice = old_apps.get_model('polls', 'Choice')
        Question.objects.bulk_create([
            Question(
                id=1,
                question_text='Who loves cheese the most?',
                pub_date=datetime.datetime(
                    2017,
                    3,
                    4,
                    12,
                    13,
                    tzinfo=datetime.timezone.utc,
                ),
            ),
            Question(
                id=2,
                question_text='What word will be censored?',
                pub_date=datetime.datetime(
                    2017,
                    5,
                    6,
                    13,
                    18,
                    tzinfo=datetime.timezone.utc,
                ),
            ),
        ])
        Choice.objects.bulk_create([
            Choice(id=1, question_id=1, choice_text='me'),
            Choice(id=2, question_id=1, choice_text='you'),
            Choice(id=3, question_id=2, choice_text='foo'),
            Choice(id=4, question_id=2, choice_text='cheese'),
            Choice(id=5, question_id=2, choice_text='bar'),
        ])

        apps = migrator.migrate_to(self.migrate_to)
        Question = apps.get_model('polls', 'Question')
        Choice = apps.get_model('polls', 'Choice')
        assert (
            Question.objects.get(id=1).question_text
            == 'Who loves ****** the most?'
        )
        assert (
            Question.objects.get(id=2).question_text
            == 'What word will be censored?'
        )
        assert Choice.objects.get(choice_text='******').id == 4

    def test_raises_ValueError_when_any_text_contain_Gjetost_mention(
            self,
            migrator,
    ):
        old_apps = migrator.migrate_from(self.migrate_from)
        Question = old_apps.get_model('polls', 'Question')
        Choice = old_apps.get_model('polls', 'Choice')
        Question.objects.create(
            id=1,
            question_text='What is the best drink to Gjetost?',
            pub_date=datetime.datetime(
                2017,
                3,
                4,
                12,
                13,
                tzinfo=datetime.timezone.utc,
            ),
        )
        Choice.objects.bulk_create([
            Choice(question_id=1, choice_text='Coffee'),
            Choice(question_id=1, choice_text='Milk'),
        ])

        with pytest.raises(ValueError, match='G|gjetost'):
            migrator.migrate_to(self.migrate_to)
