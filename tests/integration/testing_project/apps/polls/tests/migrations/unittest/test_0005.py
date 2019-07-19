import datetime

from unittest import skip

import pytest

from apps.polls import enums
from django.db.migrations.exceptions import IrreversibleError
from django.test import tag
from test_migrations.test_cases.unittest import MigrationTestCase


@pytest.mark.unittest
class Migration0005TestMixin:
    migrate_from = '0004_populate_question_difficulty_level_field'
    migrate_to = '0005_censor_cheesy_words'
    apps_module = 'apps'



class TestMigration0005_0(Migration0005TestMixin, MigrationTestCase):
    def setup_before_migration(self, apps):
        Question = apps.get_model('polls', 'Question')
        Choice = apps.get_model('polls', 'Choice')
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


    def test_cheesy_words_are_censored_in_Question_and_Choice_instances(self):
        Question = self.apps.get_model('polls', 'Question')
        Choice = self.apps.get_model('polls', 'Choice')
        assert (
            Question.objects.get(id=1).question_text
            == 'Who loves ****** the most?'
        )
        assert (
            Question.objects.get(id=2).question_text
            == 'What word will be censored?'
        )
        assert Choice.objects.get(choice_text='******').id == 4


@skip(
    'Currently it is not possible to assert if Exception raised in migration '
    'when using `test_migrations.test_cases.unittest.MigrationTestCase`'
)
class TestMigration0005_1(Migration0005TestMixin, MigrationTestCase):
    def setup_before_migration(self, apps):
        Question = apps.get_model('polls', 'Question')
        Choice = apps.get_model('polls', 'Choice')
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


    def test_raises_ValueError_when_any_text_contain_Gjetost_mention(self):
        """
        How to assert if Exception raised without manually
        managing `migrator` in each test.
        """
