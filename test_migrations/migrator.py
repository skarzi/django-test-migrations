"""Module with class that make testing django migrations easier.

Based on:
+ https://gist.github.com/asfaltboy/b3e6f9b5d95af8ba2cc46f2ba6eae5e2
+ https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations
"""
from django.core.management import call_command
from django.db import connection as db_connection
from django.db.migrations.executor import MigrationExecutor


class Migrator:
    """Control migrations for unit tests purposes.

    Notes
    -----
    Using this class has few weak points:
    + it doesn't support factoryboy
    + it's hard to assert exceptions occured during performing migration
    + it doesn't detect and update `settings.MIGRATION_MODULES`
      for migration tests
    """
    call_first_error_template = 'Call `.{method_name}()` first.'

    def __init__(self, connection=None, progress_callback=None):
        connection = connection or db_connection
        self.migration_executor = MigrationExecutor(
            connection,
            progress_callback,
        )
        self.migrate_from_state = None
        self.migrate_to_state = None

    def migrate_from(self, targets, **kwargs):
        """Migrate to the state before the migration being tested.
        """
        self.migrate_from_state = self.migration_executor.migrate(
            targets,
            **kwargs
        )
        return self.migrate_from_state.apps

    def migrate_to(self, targets, **kwargs):
        """Migrate to the state of the migration being tests.

        This method should be runned after `.migrate_from()`.
        """
        assertion_message = self.call_first_error_template.format(
            method_name='migrate_from',
        )
        assert self.migrate_from_state is not None, assertion_message

        self.migration_executor.loader.build_graph()
        self.migrate_to_state = self.migration_executor.migrate(
            targets,
            **kwargs
        )
        return self.migrate_to_state.apps

    def migrate_forward(self):
        """Flush database and migrate forward all the way.
        """
        # TODO: `flush` is using here, because `migrate` command call will
        # fail because of many factors, for instance some Exception might be
        # raised in migration when some data are present in table.
        # However it should be handled more gently, multiple db support etc,
        # refer to:
        # https://github.com/django/django/blob/master/django/test/testcases.py#L1028
        call_command('flush', verbosity=0, interactive=False)
        self.migrate_from_state = None
        self.migrate_to_state = None
