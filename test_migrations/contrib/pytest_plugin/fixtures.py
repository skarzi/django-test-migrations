import pytest


@pytest.fixture
def migrator(request):
    """Fixture used for Django's migrations testing.

    All tests using `migrator` fixture will be marked as Django's
    migrations tests.

    Examples
    --------
    >>> def test_migration_0006_update_some_field_values(migrator):
    ...     old_apps = migrator.migrate_from(
    ...         [('some_app', '0021_some_migration')],
    ...     )
    ...     SomeModel = old_apps.get_model('some_app', 'SomeModel')
    ...     # populate data using SomeModel
    ...     apps = migrator.migrate_to([('some_app', '0022_magic_migration')])
    ...     SomeModel = apps.get_model('some_app', 'SomeModel')
    ...     # get instances and perform asserts
    """
    # TODO: why it cannot be imported on the top of file when running
    # pytest's related tests on "django<2.2"?
    from test_migrations.migrator import Migrator

    _migrator = Migrator()
    request.addfinalizer(_migrator.clean)
    return _migrator
