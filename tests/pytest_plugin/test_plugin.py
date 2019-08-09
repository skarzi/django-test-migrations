import os

import pytest


@pytest.fixture
def test_dir(testdir):
    files_to_add = ['pytest.ini', 'conftest.py']  # , 'settings.py']
    for filename in files_to_add:
        testdir.copy_example(filename)
    return testdir


@pytest.mark.parametrize('initial_nomigrations_value', [
    None,
    '--migrations',
    '--nomigrations',
])
def test_set_nomigrations_to_False_when_run_with_test_migrations_option(
        test_dir,
        initial_nomigrations_value,
):
    args = ['--test-migrations']
    if initial_nomigrations_value:
        args.insert(0, initial_nomigrations_value)
    result = test_dir.runpytest(*args)
    pytest_sessionstart_hook_call = result.reprec.getcall(
        'pytest_sessionstart',
    )
    session = pytest_sessionstart_hook_call.session
    assert session.config.getoption('nomigrations') is False


def test_mark_item_with_migration_marker_if_migrator_fixture_requested(
        test_dir,
):
    test_dir.copy_example('test_using_migrator_fixture.py')
    result = test_dir.runpytest()
    # use `pytest_runtest_setup` hook, because above defined test
    # won't runned because it uses `migrator` fixture, so it's marked
    # with `migration` marker which implies `pytest_runtest_call`
    # won't be called for this item
    pytest_runtest_setup_hook_call = result.reprec.getcall(
        'pytest_runtest_setup',
    )
    migration_marker = pytest_runtest_setup_hook_call.item.get_closest_marker(
        'migration',
        None,
    )
    assert migration_marker is not None


def test_item_marked_with_migration_marker_request_transactional_db_fixture(
        test_dir,
):
    test_dir.copy_example('test_marked_with_migration_marker.py')
    result = test_dir.runpytest_subprocess('--test-migrations', '--setup-show')
    result.assert_outcomes(passed=1)
    result.stdout.re_match_lines(['\s*SETUP    F transactional_db'])


def test_item_marked_with_migration_marker_are_skipped_if_CLI_option_test_migrations_not_passed(
        test_dir,
):
    # skipped
    test_dir.copy_example('test_marked_with_migration_marker.py')
    test_dir.copy_example('test_using_migrator_fixture.py')
    # passed
    test_dir.copy_example('test_not_related_to_test_migrations.py')
    result = test_dir.runpytest_subprocess()
    result.assert_outcomes(passed=1, skipped=2)


def test_item_marked_with_migration_marker_are_not_skipped_if_CLI_option_test_migrations_passed(
        test_dir,
):
    # passed
    test_dir.copy_example('test_marked_with_migration_marker.py')
    test_dir.copy_example('test_using_migrator_fixture.py')
    # skipped
    test_dir.copy_example('test_not_related_to_test_migrations.py')
    result = test_dir.runpytest_subprocess('--test-migrations')
    result.assert_outcomes(passed=2, skipped=1)
