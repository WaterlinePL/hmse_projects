from enum import auto

from strenum import StrEnum


class SimulationMode(StrEnum):
    SIMPLE_COUPLING = auto()
    WITH_FEEDBACK = auto()
