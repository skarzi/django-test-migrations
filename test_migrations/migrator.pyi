import typing

from django.apps.registry import Apps
from django.db import DefaultConnectionProxy
from django.db.backends.base.client import BaseDatabaseClient
from django.db.migrations import Migration
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import ProjectState

TargetType = typing.Tuple[str, typing.Optional[str]]


class Migrator:
    call_first_erro_template: typing.ClassVar[str]

    migration_executor: MigrationExecutor
    migrate_from_state: typing.Optional[ProjectState]
    migrate_to_state: typing.Optional[ProjectState]

    def __init__(
            self,
            connection: typing.Union[
                DefaultConnectionProxy,
                BaseDatabaseClient,
                None,
            ],
            progress_callback: typing.Optional[
                typing.Callable[
                    [str, typing.Optional[Migration], bool],
                    None,
                ],
            ],
    ):
        ...

    def migrate_from(
            self,
            targets: typing.Iterable[TargetType],
            **kwargs: typing.Any,
    ) -> Apps:
        ...

    def migrate_to(
            self,
            targets: typing.Iterable[TargetType],
            **kwargs: typing.Any,
    ) -> Apps:
        ...

    def migrate_forward(self) -> None: ...
