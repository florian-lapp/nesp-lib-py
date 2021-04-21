import enum

class AlarmStatus(enum.Enum) :
    """Alarm status of a pump."""

    RESET = enum.auto()
    """Pump was reset (power was interrupted)."""
    STALLED = enum.auto()
    """Pump motor stalled."""
    TIMEOUT = enum.auto()
    """Safe mode communication timeout occurred."""
    ERROR = enum.auto()
    """Pumping program error occurred."""
    RANGE = enum.auto()
    """Pumping program phase is out of range."""