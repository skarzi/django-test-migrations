import datetime

from django.test import tag

from apps.polls import enums


@tag('pytest')
class TestMigration0004:
    migrate_from = [('polls', '0002_question_is_hard')]
    migrate_to = [('polls', '0004_populate_question_difficulty_level_field')]

    def test_difficulty_level_field_has_proper_values(self, migrator):
        old_apps = migrator.migrate_from(self.migrate_from)
        Question = old_apps.get_model('polls', 'Question')
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

        apps = migrator.migrate_to(self.migrate_to)
        Question = apps.get_model('polls', 'Question')
        assert (
            Question.objects.get(question_text='Hard').difficulty_level
            == enums.DifficultyLevel.HARD
        )
        assert (
            Question.objects.get(question_text='Medium').difficulty_level
            == enums.DifficultyLevel.MEDIUM
        )

    def test_is_hard_field_has_proper_values_when_reversing_migration(
            self,
            migrator,
    ):
        old_apps = migrator.migrate_from(self.migrate_to)
        Question = old_apps.get_model('polls', 'Question')
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

        apps = migrator.migrate_to(self.migrate_from)
        Question = apps.get_model('polls', 'Question')
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
