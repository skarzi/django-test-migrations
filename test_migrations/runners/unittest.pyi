import typing

from django.test.runner import DiscoverRunner as DjangoDiscoverRunner


class MigrationTestRunnerMixin:
    def __init__(
            self,
            *args: typing.Any,
            tags: typing.Optional[typing.Iterable[str]] = ...,
            exclude_tags: typing.Optional[typing.Iterable[str]] = ...,
            **kwargs: typing.Any,
    ):
        ...


class DiscoverRunner(MigrationTestRunnerMixin, DjangoDiscoverRunner):
    pass
