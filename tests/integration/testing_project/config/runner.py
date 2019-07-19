import typing

from argparse import ArgumentParser


class PytestTestRunner:
    """Runs pytest to discover and run tests.
    """

    def __init__(
            self,
            pattern: typing.Optional[str] = None,
            top_level: typing.Optional[str] = None,
            verbosity: int = 1,
            interactive: bool = True,
            failfast: bool = False,
            keepdb: bool = False,
            reverse: bool = False,
            debug_mode: bool = False,
            debug_sql: bool = False,
            parallel: int = 0,
            tags: typing.Optional[typing.Sequence[str]] = None,
            exclude_tags: typing.Optional[typing.Sequence[str]] = None,
            **kwargs: typing.Any,
    ):
        self.pattern = pattern
        self.top_level = top_level
        self.verbosity = verbosity
        self.interactive = interactive
        self.failfast = failfast
        self.keepdb = keepdb
        self.reverse = reverse
        self.debug_mode = debug_mode
        self.debug_sql = debug_sql
        self.parallel = parallel
        self.tags = set(tags or list())
        self.exclude_tags = set(exclude_tags or list())

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        parser.add_argument(
            '-k',
            '--keepdb',
            action='store_true',
            dest='keepdb',
            help='Preserves the tests DB between runs.',
        )
        parser.add_argument(
            '--tag',
            action='append',
            dest='tags',
            help=(
                'Run only tests with the specified tag. '
                'Can be used multiple times.'
            ),
        )
        parser.add_argument(
            '--exclude-tag',
            action='append',
            dest='exclude_tags',
            help=(
                'Do not run tests with the specified tag. '
                'Can be used multiple times.'
            ),
        )

    def run_tests(
            self,
            test_labels: typing.Sequence[str],
            extra_tests: typing.Optional[typing.Sequence[typing.Any]] = None,
            **kwargs: typing.Any,
    ) -> int:
        """
        Run pytest and return the exitcode.
        It translates some of Django's test command option to pytest's.
        """
        import pytest
        argv = list()

        if self.failfast:
            argv.append('--exitfirst')

        if self.parallel:
            argv.append('--numprocesses={}'.format(self.parallel))

        if self.keepdb:
            argv.append('--reuse-db')

        if self.verbosity == 0:
            argv.append('--quiet')
        elif self.verbosity == 2:
            argv.append('--verbose')
        elif self.verbosity == 3:
            argv.append('-vv')

        argv.extend(test_labels)
        return pytest.main(argv)
