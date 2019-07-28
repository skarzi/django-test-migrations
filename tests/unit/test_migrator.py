import pytest

from test_migrations.migrator import Migrator


@pytest.fixture
def migrator(transactional_db, mocker):
    _migrator = Migrator()
    mocker.patch.object(_migrator, 'migration_executor')
    return _migrator


class TestMigrator:
    testing_targets = [('app', '0001_initial')]

    def test_migrate_from_calls_migrate_on_migration_executor(self, migrator):
        migrator.migrate_from(self.testing_targets)
        migrator.migration_executor.migrate.assert_called_once_with(
            self.testing_targets,
        )
        assert migrator.migration_executor.migrate_from_state is not None

    def test_migrate_to_raises_assertion_error_when_migrate_from_not_called(
            self,
            migrator,
    ):
        assert migrator.migrate_from_state is None
        with pytest.raises(AssertionError):
            migrator.migrate_to(self.testing_targets)

    def test_migrate_to_calls_reload_migrations(self, migrator, mocker):
        migrator.migrate_from_state = mocker.MagicMock()
        migrator.migrate_to(self.testing_targets)
        migrator.migration_executor.loader.build_graph.assert_called_once()
        migrator.migration_executor.migrate.assert_called_once_with(
            self.testing_targets,
        )
        assert migrator.migration_executor.migrate_to_state is not None

    def test_migrate_forward_calls_call_command_when_migrate_to_applied(
            self,
            migrator,
            mocker,
    ):
        migrator.migrate_to_state = mocker.MagicMock()
        call_command_mock = mocker.patch(
            'test_migrations.migrator.call_command',
        )
        migrator.migrate_forward()
        call_command_mock.assert_called_once_with(
            'flush',
            verbosity=0,
            interactive=False,
        )
