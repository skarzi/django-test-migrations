import typing

from django.test import runner

from test_migrations import settings


class MigrationTestRunnerMixin:
    def __init__(
            self,
            *args: typing.Any,
            tags: typing.Optional[typing.Sequence[str]] = None,
            exclude_tags: typing.Optional[typing.Sequence[str]] = None,
            **kwargs: typing.Any,
    ):
        tags = tags or list()
        if settings.MIGRATIONS_TEST_MARKER not in tags:
            exclude_tags = set(exclude_tags or list())
            exclude_tags.add(settings.MIGRATIONS_TEST_MARKER)
        super().__init__(*args, tags=tags, exclude_tags=exclude_tags, **kwargs)


class DiscoverRunner(MigrationTestRunnerMixin, runner.DiscoverRunner):
    """DiscoverRunner ignoring all migration tests by default.

    To run migrations test request only tests marked with
    `settings.MIGRATIONS_TEST_MARKER` tag.
    """
