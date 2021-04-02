__all__ = [
    'Exception',
    'InternalException',
    'IdentityException',
    'ChecksumException',
    'ChecksumRequestException',
    'ChecksumReplyException',
    'StateException',
    'StatusAlarmException'
]

from .alarm import Alarm

import abc

class Exception(Exception, abc.ABC) :
    """Generic exception."""
    pass

class InternalException(Exception) :
    """
    Exception that indicates an internal error.

    This exception should never occur and therefore is not needed to catch.
    """
    pass

class IdentityException(Exception) :
    """Exception that indicates that an identity is wrong."""

class ChecksumException(Exception, abc.ABC) :
    """
    Exception that indicates that the checksum of a request or a reply is wrong.

    The reason for this exception is an unstable communication from the host to the pump or from the
    pump to the host.
    """
    pass

class ChecksumRequestException(ChecksumException) :
    """
    Exception that indicates that the checksum of a request is wrong.

    The reason for this exception is an unstable communication from the host to the pump.
    """
    pass

class ChecksumReplyException(Exception) :
    """
    Exception that indicates that the checksum of a reply is wrong.

    The reason for this exception is an unstable communication from the pump to the host.
    """
    pass

class StateException(Exception) :
    """
    Exception that indicates that a method was invoked in a state when it is not allowed to be
    invoked.
    """
    pass

class StatusAlarmException(Exception) :
    """Exception that indicates that the pump has an alarm status."""

    def __init__(self, alarm : Alarm) -> None :
        """Constructs an exception with the given alarm."""
        self.__alarm = alarm

    @property
    def alarm(self) -> Alarm :
        """Gets the alarm of the exception."""
        return self.__alarm