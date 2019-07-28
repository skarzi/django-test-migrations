import typing

from django.apps.registry import Apps

from . import migrator as _migrator

MigrationTargetType = typing.Union[
    typing.Iterable[_migrator.TargetType],
    str,
    None,
]


class MigrationTestMixin:
    migrator_config: typing.ClassVar[typing.Dict[str, typing.Any]]
    missing_migrate_targets_error_template: typing.ClassVar[str]
    apps_module: typing.ClassVar[str]

    migrate_from: MigrationTargetType
    migrate_to: MigrationTargetType
    migrator: _migrator.Migrator
    old_apps: Apps
    apps: Apps

    @property
    def current_app_name(self) -> str: ...

    def setup_test(self) -> None: ...

    def teardown_test(self) -> None: ...

    def setup_before_migration(self, apps: Apps) -> None: ...

    def assert_migration_targets_defined(self) -> None: ...

    def process_migration_target(
            self,
            migration_target: MigrationTargetType,
    ) -> typing.Iterable[_migrator.TargetType]:
        ...
