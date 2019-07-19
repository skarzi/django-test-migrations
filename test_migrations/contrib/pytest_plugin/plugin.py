import pytest

from test_migrations import settings

from .fixtures import migrator  # pylint: disable=W0611

pytest_plugins = ['pytest_django']  # pylint: disable=C0103


def pytest_load_initial_conftests(early_config):
    # Register the marks
    early_config.addinivalue_line(
        'markers',
        (
            f"{settings.MIGRATIONS_TEST_MARKER}: Mark the test as "
            "Django's migration test. Dynamically add `transactional_db` "
            "fixture to marked item. Migration tests are runned only when "
            "`--test-migrations` pytest's CLI option passed."
        ),
    )
    # TODO: why I wrote this if statement?
    # if early_config.getoption('test_migrations', False):
    #     markexpr = early_config.option.markexp
    #     if markexpr:
    #         print(markexpr)
    #     early_config.option.markexpr = 'migration'


def pytest_addoption(parser):
    """Add option for running migration tests.
    """
    group = parser.getgroup('django_test_migrations')
    group._addoption(  # pylint: disable=W0212
        '--test-migrations',
        action='store_true',
        dest='test_migrations',
        default=False,
        help=(
            "Run Django's migrations tests. It does the following: "
            " ensure migrations are enabled, skip all test not marked with "
            f"`{settings.MIGRATIONS_TEST_MARKER}` marker."
        )
    )


def pytest_sessionstart(session):
    if session.config.getoption('test_migrations', False):
        # TODO: consider raising AssertionError when `nomigration` falsy
        session.config.option.nomigrations = False


def pytest_collection_modifyitems(session, items):
    migration_test_skip_marker = pytest.mark.skip(
        reason=(
            'No migration test skipped, because`--test-migration` option '
            'passed.'
        ),
    )
    for item in items:
        # mark all tests using `migrator` fixture with `MIGRATION_TEST_MARKER`
        if 'migrator' in getattr(item, 'fixturenames', list()):
            item.add_marker(settings.MIGRATIONS_TEST_MARKER)
        # skip all no migration tests when option `--test-migrations` passed
        if (
                session.config.getoption('test_migrations', False)
                and not item.get_closest_marker(settings.MIGRATIONS_TEST_MARKER)
        ):
            item.add_marker(migration_test_skip_marker)


@pytest.fixture(autouse=True, scope='function')
def _django_migration_marker(request):
    """Implement the migration marker, internal to `django_test_migrations`.

    This will dynamically request the `transactional_db` fixture
    and skip tests marked with migration marker if not
    explicitly requested by passing `--test-migrations` option.
    """
    marker = request.node.get_closest_marker(settings.MIGRATIONS_TEST_MARKER)
    if marker:
        if request.config.getoption('test_migrations', False):
            request.getfixturevalue('transactional_db')
        else:
            pytest.skip(
                msg=(
                    'Migration tests can require `migrations` enabled and can '
                    'be slow hence they should be ran separetly with pytest '
                    '`--test-migrations` option.'
                ),
            )
