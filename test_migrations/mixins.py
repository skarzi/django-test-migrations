import typing

from django.apps import apps as django_apps
from django.apps.registry import Apps

from . import migrator

MigrateTarget = typing.Union[str, typing.Iterable[migrator.Target]]


class MigrationTestMixin:
    """Mixing that make django migrations testing easier.

    Parameters
    ----------
    migrate_from
        migration applied before `.migrate_to`
    migrate_to
        tested migration
    migrator_config
        dict with `migrator.Migrator` init arguments
    apps_module
        name of module where django apps are located
    """
    migrate_from: MigrateTarget
    migrate_to: MigrateTarget
    migrator_config: typing.Mapping[str, typing.Any] = {
        'connection': None,
        'progress_callback': None,
    }
    missing_migrate_targets_error_template: str = (
        '"{class_name}" must define `.migrate_from` and `.migrate_to` '
        'properties.'
    )
    apps_module: str = ''

    @property
    def current_app_name(self) -> str:
        app_config = django_apps.get_containing_app_config(
            self.__class__.__module__,
        )
        name = None
        if app_config:
            name = app_config.name
            module_prefix = self.apps_module + '.'
            if name.startswith(module_prefix):
                name = name[len(module_prefix):]
        return name

    def setup_test(self) -> None:
        self.assert_migrate_targets_defined()
        self.migrate_from = self.process_migration_target(self.migrate_from)
        self.migrate_to = self.process_migration_target(self.migrate_to)
        self.migrator = migrator.Migrator(**self.migrator_config)
        # Reverse to the previous migration
        self.old_apps = self.migrator.migrate_from(self.migrate_from)
        self.setup_before_migration(self.old_apps)
        # Run the migration being tested
        self.apps = self.migrator.migrate_to(self.migrate_to)

    def teardown_test(self) -> None:
        self.migrator.migrate_forward()

    def setup_before_migration(self, apps: Apps) -> None:
        """Populate data before performing tested migration.

        This method is called just after applying `migrate_from` migration
        and just before running `migrate_to` migration.
        Use `apps.get_model()` to get model class and create instances.
        """

    def assert_migrate_targets_defined(self) -> None:
        has_migrate_from = getattr(self, 'migrate_from', None)
        has_migrate_to = getattr(self, 'migrate_to', None)
        assertion_message = self.missing_migrate_targets_error_template.format(
            class_name=self.__class__.__qualname__,
        )
        assert has_migrate_from and has_migrate_to, assertion_message

    def process_migration_target(
            self,
            migrate_target: MigrateTarget,
    ) -> migrator.Target:
        if isinstance(migrate_target, str):
            return [(self.current_app_name, migrate_target)]
        return migrate_target
