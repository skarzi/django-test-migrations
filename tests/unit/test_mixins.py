import pytest

from test_migrations import mixins


class MigrationTestEmpty(mixins.MigrationTestMixin):
    pass


class MigrationTestWithMigrateFrom(mixins.MigrationTestMixin):
    migrate_from = '0001_initial'


class MigrationTestWithMigrateTo(mixins.MigrationTestMixin):
    migrate_to = '0004_add_some_field_to_some_model'


class MigrationTestWithMigrateTargetEqualsToNone(mixins.MigrationTestMixin):
    migrate_from = None
    migrate_to = '0004_add_some_field_to_some_model'


class MigrationTestWithBothMigrateTargets(mixins.MigrationTestMixin):
    migrate_from = '0001_initial'
    migrate_to = '0004_add_some_field_to_some_model'


class MigrationTestWithBothFullMigrateTargets(mixins.MigrationTestMixin):
    migrate_from = [('test_app', '0001_initial')]
    migrate_to = [('test_app', '0004_add_some_field_to_some_model')]


class TestMigrationTestMixin:
    def test_current_app_name_return_None_when_app_not_registered(
            self,
            mocker,
    ):
        mocker.patch(
            'test_migrations.mixins.django_apps.get_containing_app_config',
            return_value=None,
        )
        instance = MigrationTestWithBothMigrateTargets()
        assert instance.current_app_name is None

    def test_current_app_name_return_app_name_when_app_registered_not_stored_in_module(
            self,
            mocker,
    ):
        app_name = 'testing_app_name'
        app_config_getter_mock = mocker.patch(
            'test_migrations.mixins.django_apps.get_containing_app_config',
        )
        app_config_getter_mock.return_value.name = app_name
        instance = MigrationTestWithBothMigrateTargets()
        assert instance.current_app_name == app_name

    @pytest.mark.parametrize('app_name, expected_app_name', [
        ('app_name',) * 2,
        ('testing_module.app_name', 'app_name'),
    ])
    def test_current_app_name_return_app_name_when_app_registered_and_stored_in_module(
            self,
            mocker,
            app_name,
            expected_app_name,
    ):
        app_config_getter_mock = mocker.patch(
            'test_migrations.mixins.django_apps.get_containing_app_config',
        )
        app_config_getter_mock.return_value.name = app_name
        instance = MigrationTestWithBothMigrateTargets()
        instance.apps_module = 'testing_module'
        assert instance.current_app_name == expected_app_name

    @pytest.mark.parametrize('instance', [
        MigrationTestEmpty(),
        MigrationTestWithMigrateFrom(),
        MigrationTestWithMigrateTo(),
        MigrationTestWithMigrateTargetEqualsToNone(),
    ])
    def test_assert_migration_targets_defined_raises_AssertionError(
            self,
            instance,
    ):
        with pytest.raises(AssertionError):
            instance.assert_migration_targets_defined()

    def test_assert_migration_targets_defined_dont_pass_when_targets_defined(
            self,
    ):
        instance = MigrationTestWithBothMigrateTargets()
        assert instance.assert_migration_targets_defined() is None

    def test_process_migration_target(self):
        instance = MigrationTestWithBothMigrateTargets()
        str_target = '0001_initial'
        expected = [(None, str_target)]
        assert instance.process_migration_target(str_target) == expected
        tuple_target = [('app', str_target), ('other_app', '0090_alter_field')]
        assert instance.process_migration_target(tuple_target) == tuple_target

    def test_teardown_test_calls_migrator_clean(self, mocker):
        migration_test = MigrationTestWithBothMigrateTargets()
        migration_test.migrator = mocker.Mock()
        migration_test.teardown_test()
        # `.assert_called_once()` was added in python 3.6
        migration_test.migrator.clean.assert_called_once_with()

    def test_setup_test_calls_proper_migrator_methods_and_setup_before_migration(
            self,
            mocker,
    ):
        migrator_mock = mocker.patch(
            'test_migrations.mixins.migrator.Migrator',
        )
        migrator_mock = migrator_mock.return_value
        migration_test = MigrationTestWithBothFullMigrateTargets()
        migration_test.setup_before_migration = mocker.Mock()
        migration_test.setup_test()

        migrator_mock.migrate_from.assert_called_once_with(
            migration_test.migrate_from,
        )
        migration_test.setup_before_migration.assert_called_once_with(
            migrator_mock.migrate_from.return_value,
        )
        migrator_mock.migrate_to.assert_called_once_with(
            migration_test.migrate_to,
        )
        assert migration_test.apps == migrator_mock.migrate_to.return_value
