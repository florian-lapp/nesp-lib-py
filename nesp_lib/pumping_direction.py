import enum

class PumpingDirection(enum.Enum) :
    """Pumping direction of a pump."""

    INFUSE = enum.auto()
    """Infuse."""
    WITHDRAW = enum.auto()
    """Withdraw."""