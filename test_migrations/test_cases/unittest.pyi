from django.test import TransactionTestCase

from test_migrations.mixins import MigrationTestMixin


class MigrationTestCase(MigrationTestMixin, TransactionTestCase):
    def setUp(self) -> None: ...

    def tearDown(self) -> None: ...
