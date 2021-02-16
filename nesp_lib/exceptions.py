__all__ = [
    'Exception',
    'ExceptionInternal',
    'ExceptionIdentity',
    'ExceptionChecksum',
    'ExceptionChecksumRequest',
    'ExceptionChecksumReply',
    'ExceptionState',
    'ExceptionStatusAlarm'
]

from .alarm import Alarm

import abc

class Exception(Exception, abc.ABC) :
    """Generic exception."""
    pass

class ExceptionInternal(Exception) :
    """
    Exception that indicates an internal error.

    This exception should never occur and therefore is not needed to catch.
    """
    pass

class ExceptionIdentity(Exception) :
    """Exception that indicates that an identity is wrong."""

class ExceptionChecksum(Exception, abc.ABC) :
    """
    Exception that indicates that the checksum of a request or a reply is wrong.

    The reason for this exception is an unstable communication from the host to the pump or from the
    pump to the host.
    """
    pass

class ExceptionChecksumRequest(ExceptionChecksum) :
    """
    Exception that indicates that the checksum of a request is wrong.

    The reason for this exception is an unstable communication from the host to the pump.
    """
    pass

class ExceptionChecksumReply(Exception) :
    """
    Exception that indicates that the checksum of a reply is wrong.

    The reason for this exception is an unstable communication from the pump to the host.
    """
    pass

class ExceptionState(Exception) :
    """
    Exception that indicates that a method was invoked in a state when it is not allowed to be
    invoked.
    """
    pass

class ExceptionStatusAlarm(Exception) :
    """Exception that indicates that the pump has an alarm status."""

    def __init__(self, alarm : Alarm) -> None :
        """Constructs an exception with the given alarm."""
        self.__alarm = alarm

    @property
    def alarm(self) -> Alarm :
        """Gets the alarm of the exception."""
        return self.__alarm