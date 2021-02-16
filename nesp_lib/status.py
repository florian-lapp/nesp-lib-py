import enum

class Status(enum.Enum) :
    """Status of a pump."""

    # Pump infusing.
    INFUSING = enum.auto()
    # Pump withdrawing.
    WITHDRAWING = enum.auto()
    # Pump purging.
    PURGING = enum.auto()
    # Pumping stopped.
    STOPPED = enum.auto()
    # Pumping paused.
    PAUSED = enum.auto()
    # Pumping program sleeping (Pause phase).
    SLEEPING = enum.auto()
    # Pumping program waiting (for a user input).
    WAITING = enum.auto()