import enum

class Alarm(enum.Enum) :
    """Alarm of a pump."""

    # Pump was reset (power was interrupted).
    RESET = enum.auto()
    # Pump motor stalled.
    STALLED = enum.auto()
    # Safe mode communication timeout occurred.
    TIMEOUT = enum.auto()
    # Pumping program error occurred.
    ERROR = enum.auto()
    # Pumping program phase is out of range.
    RANGE = enum.auto()