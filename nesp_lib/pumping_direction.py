import enum

class PumpingDirection(enum.Enum) :
    """Pumping direction of a pump."""

    # Infuse.
    INFUSE = enum.auto()
    # Withdraw.
    WITHDRAW = enum.auto()