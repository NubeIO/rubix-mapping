import enum


class MappingState(enum.Enum):
    MAPPED = 'Mapped',
    BROKEN = 'Broken'


class MapType(enum.Enum):
    GENERIC = 'Generic'
    BACNET = 'Bacnet'
