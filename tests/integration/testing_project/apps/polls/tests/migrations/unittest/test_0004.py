import datetime

import pytest

from apps.polls import enums

from test_migrations.test_cases.unittest import MigrationTestCase


@pytest.mark.unittest
class TestMigration0004_0(MigrationTestCase):
    migrate_from = '0002_question_is_hard'
    migrate_to = '0004_populate_question_difficulty_level_field'
    apps_module = 'apps'

    def setup_before_migration(self, apps):
        Question = apps.get_model('polls', 'Question')
        Question.objects.bulk_create([
            Question(
                question_text='Hard',
                pub_date=datetime.datetime(
                    2017,
                    3,
                    4,
                    12,
                    13,
                    tzinfo=datetime.timezone.utc,
                ),
                is_hard=True,
            ),
            Question(
                question_text='Medium',
                pub_date=datetime.datetime(
                    2017,
                    5,
                    6,
                    13,
                    18,
                    tzinfo=datetime.timezone.utc,
                ),
                is_hard=False,
            ),
        ])

    def test_difficulty_level_field_has_proper_values(self):
        Question = self.apps.get_model('polls', 'Question')
        self.assertEqual(
            Question.objects.get(question_text='Hard').difficulty_level,
            enums.DifficultyLevel.HARD,
        )
        self.assertEqual(
            Question.objects.get(question_text='Medium').difficulty_level,
            enums.DifficultyLevel.MEDIUM,
        )


@pytest.mark.unittest
class TestMigration0004_1(MigrationTestCase):
    migrate_from = '0004_populate_question_difficulty_level_field'
    migrate_to = '0002_question_is_hard'
    apps_module = 'apps'

    def setup_before_migration(self, apps):
        Question = apps.get_model('polls', 'Question')
        Question.objects.bulk_create([
            Question(
                id=i,
                question_text=member.name,
                pub_date=datetime.datetime(
                    2017,
                    3,
                    4,
                    12,
                    i,
                    tzinfo=datetime.timezone.utc,
                ),
                difficulty_level=member.value,
            )
            for i, member in enumerate(enums.DifficultyLevel, 1)
        ])

    def test_is_hard_field_has_proper_values_when_reversing_migration(self):
        Question = self.apps.get_model('polls', 'Question')
        easy_questions = set(
            Question.objects.filter(is_hard=False).values_list('id', flat=True)
        )
        assert len(easy_questions) == 2
        assert easy_questions == {1, 2}
        hard_questions = set(
            Question.objects.filter(is_hard=True).values_list('id', flat=True)
        )
        assert len(hard_questions) == 2
        assert hard_questions == {3, 4}
