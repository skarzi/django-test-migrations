from django.test import runner

from test_migrations import constants


class MigrationTestRunnerMixin:
    def __init__(self, *args, tags=None, exclude_tags=None, **kwargs):
        tags = tags or list()
        if constants.MIGRATIONS_TEST_MARKER not in tags:
            exclude_tags = set(exclude_tags or list())
            exclude_tags.add(constants.MIGRATIONS_TEST_MARKER)
        super().__init__(*args, tags=tags, exclude_tags=exclude_tags, **kwargs)


class DiscoverRunner(MigrationTestRunnerMixin, runner.DiscoverRunner):
    """DiscoverRunner ignoring all migration tests by default.

    To run migrations test request only tests marked with
    `constants.MIGRATIONS_TEST_MARKER` tag.
    """
