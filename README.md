# Django Test Migrations

[![Build Status](https://travis-ci.org/skarzi/django-test-migrations.svg?branch=master)](https://travis-ci.org/skarzi/django-test-migrations)
[![Coverage Status](https://coveralls.io/repos/github/skarzi/django-test-migrations/badge.svg)](https://coveralls.io/github/skarzi/django-test-migrations)

> This project is no longer maintained, switch to [`wemake-services/django-test-migrations`](https://github.com/wemake-services/django-test-migrations), which is in active development.

Django migration testing utilities

These testing utilities were created after experiencing many issues during
Django project deployments, caused by migrations.

Testing migrations with just Django or pytest (even with pytests-django) is
not easily done.
Django's test runner creates a temporary test database for us, to accomplish that
it runs all migrations before tests. This means our tests are running on the
latest version of the schema. It is impossible to verify behaviour/results
of our migrations, because the tests cannot setup data or assert conditions
before running them.

This module intends to be a solution to these problems.


## Migration Test Lifecycle

The majority of migration issues are caught while performing migrations on
staging and production environments, whose databases contain non-trivial data.
This module gives us the ability to go back to migrations that are before
our target migration (the one we want to test). Then we can
setup data and/or assert some conditions before applying the tested migration.
Finally we can validate if everything changed correctly.
The migration test lifecycle can be expressed in these 4 points:

1. Go back to start migration.
2. Setup data, assert conditions.
3. Go to target migration.
4. Asserts.


## When to test migrations?
It's super surprising, but not every migration needs tests! ;)
You do not have to test simple non-data migrations like adding a new nullable
column or adding a new table.
Generally tests of migrations that do not have any special impact on your
data can be skipped.
Tests are must-have for data migrations or schema migrations that might be
sensitive to data, such as changing constraints/types, renaming tables
and columns or building new indexes.


# Using this module

With this module migrations tests can be written in one of 2 ways:

+ as Django `TransactionTestCase` (`test_migrations.test_cases.unittest.MigrationTestCase`)
+ as function/classes using the`migrator` pytest fixture

In the following sections, we provide examples of each method.
Our example migration for these will be:
`apps.polls.migrations.0004_populate_question_difficulty_level_field`
(sample testing project can be found in `tests/integration/` directory):

```python
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
```


## Testing with `test_migrations.test_cases.unittest.MigrationTestCase`

This module provides two base test case classes, which contain some useful helpers for common tasks related to migration testing.

To create a migration test, you'll need to do the following:

1. Set `migrate_to` attribute to migrations or migration
   name that you want to test.
   If this value is string, then it is assumed that you want test
   migration from current application where tests are stored in.
   To set concrete, specific migrations or multiple migrations, pass a list of them,
   for instance:

    ```python
    [
        ('app', '0003_some_migration'),
        ('other_app', '0021_magic_happens_here'),
    ]
    ```
2. Set `migrate_from` attribute to migration/migrations that should be run
   before going to `migrate_from`.
3. Implement `setup_before_migration` method, this method can be used to
   populate data etc.

Migration tests are generally slow, so all test cases that extend
`test_migrations.test_cases.unittest.MigrationTestCase` are tagged with
`migration` tag and skipped when running tests, unless you explicitly pass
`--tag migration` to `python manage.py test` command.

Notice that you can use all assert methods from Django test case.

```python
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
```


## Using the `migrator` fixture

This is probably the most powerful way of testing migrations,
however it forces you to write a bit of boilerplate code.

All tests using `migrator` fixture are marked with the `migration` marker.

```python
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
```


## Running migration tests

This module can be run with Django's test runner or with pytest.

### Running migration tests with Django test runner

When only Django's testing utilities with bare `unittest` are used it's 
necessary to set Django's `TEST_RUNNER` setting to
`'test_migrations.runner.unittest.DiscoverRunner'`, then migrations test can
be ran using the following command:

```bash
python manage.py test --tag migration
```

### Running migrations tests with pytest

To run migrations tests with pytest use the `--test-migrations` switch:

```bash
pytest --test-migrations
```
