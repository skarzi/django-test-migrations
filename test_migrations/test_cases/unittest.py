from django.test import (
    TransactionTestCase,
    tag,
)

from test_migrations import constants
from test_migrations.mixins import MigrationTestMixin


@tag(constants.MIGRATIONS_TEST_MARKER)
class MigrationTestCase(MigrationTestMixin, TransactionTestCase):
    """TestCase for testing Django migrations.

    Examples
    --------
    >>> class TestMigration0021(MigrationTestCase):
    ...     migrate_from = '0020_some_migration'
    ...     migrate_to = [('some_app', '0021_magic_migration')]
    ...
    ...     def setup_before_migration(self, apps):
    ...         SomeModel = apps.get_model('some_app', 'SomeModel')
    ...         # populate data using SomeModel
    ...
    ...     def test_some_field_value_updated(self):
    ...         SomeModel = self.apps.get_model('some_app', 'SomeModel')
    ...         # get instances and perform asserts
    """
    def setUp(self):
        self.setup_test()

    def tearDown(self):
        self.teardown_test()
