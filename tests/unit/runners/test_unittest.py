import pytest

from test_migrations.runners import unittest as unittest_runners


class DummyTestRunner:
    def __init__(self, *args, tags=None, exclude_tags=None, **kwargs):
        self.tags = set(tags or list())
        self.exclude_tags = set(exclude_tags or list())


class DummyMigrationTestRunner(
        unittest_runners.MigrationTestRunnerMixin,
        DummyTestRunner,
):
    pass


class TestMigrationTestRunnerMixin:
    mixin_subclass = DummyMigrationTestRunner
    migrations_test_marker = 'migration'

    @pytest.fixture(autouse=True)
    def setup_test(self, settings):
        settings.MIGRATIONS_TEST_MARKER = self.migrations_test_marker

    @pytest.mark.parametrize('tags', [None, list(), ['slow', 'windows']])
    @pytest.mark.parametrize('exclude_tags', [
        None,
        list(),
        ['foo', 'bar'],
    ])
    def test_migrations_test_marker_is_added_to_excluded_tags_if_not_requested(
            self,
            tags,
            exclude_tags,
    ):
        instance = self.mixin_subclass(tags=tags, exclude_tags=exclude_tags)
        expected_exclude_tags = set(exclude_tags or list())
        expected_exclude_tags.add(self.migrations_test_marker)
        assert instance.exclude_tags == expected_exclude_tags

    @pytest.mark.parametrize('tags', [
        [migrations_test_marker],
        ['slow', migrations_test_marker, 'windows'],
    ])
    def test_migrations_test_marker_is_not_added_to_excluded_tags_if_requested(
            self,
            tags,
    ):
        instance = self.mixin_subclass(tags=tags)
        assert instance.exclude_tags == set()
