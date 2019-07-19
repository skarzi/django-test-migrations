import enum
import typing


class DifficultyLevel(enum.IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    SUPER_HARD = 4

    @classmethod
    def choices(cls) -> typing.List[typing.Tuple[int, str]]:
        return [
            (member.value, member.name.replace('_', ' ').title())
            for member in cls
        ]
