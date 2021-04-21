import enum

class Status(enum.Enum) :
    """Status of a pump."""

    INFUSING = enum.auto()
    """Pump infusing."""
    WITHDRAWING = enum.auto()
    """Pump withdrawing."""
    PURGING = enum.auto()
    """Pump purging."""
    STOPPED = enum.auto()
    """Pumping stopped."""
    PAUSED = enum.auto()
    """Pumping paused."""
    SLEEPING = enum.auto()
    """Pumping program sleeping (Pause phase)."""
    WAITING = enum.auto()
    """Pumping program waiting (for a user input)."""