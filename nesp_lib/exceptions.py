from .alarm_status import AlarmStatus

import abc

__all__ = [
    'Exception',
    'InternalException',
    'AddressException',
    'ModelException',
    'ChecksumException',
    'ChecksumRequestException',
    'ChecksumReplyException',
    'StateException',
    'StatusAlarmException'
]

class Exception(Exception, abc.ABC) :
    """Generic exception."""
    pass

class InternalException(Exception) :
    """
    Exception that indicates an internal error.

    This exception should never occur.
    """
    pass

class AddressException(Exception) :
    """Exception that indicates that an address is wrong."""
    pass

class ModelException(Exception) :
    """Exception that indicates that a model is wrong."""
    pass

class ChecksumException(Exception, abc.ABC) :
    """
    Exception that indicates that the checksum of a request or a reply is wrong.

    The reason for this exception is an unstable connection between the requester and the replier.
    """
    pass

class ChecksumRequestException(ChecksumException) :
    """
    Exception that indicates that the checksum of a request is wrong.

    The reason for this exception is an unstable connection from the requester to the replier.
    """
    pass

class ChecksumReplyException(Exception) :
    """
    Exception that indicates that the checksum of a reply is wrong.

    The reason for this exception is an unstable connection from the replier to the requester.
    """
    pass

class StateException(Exception) :
    """
    Exception that indicates that a function was invoked on an object when that object was in a
    state that prohibits the invocation of that function.
    """
    pass

class StatusAlarmException(Exception) :
    """Exception that indicates that an object is in an alarm status."""

    def __init__(self, alarm_status : AlarmStatus) -> None :
        """
        Constructs an exception.

        :param alarm_status:
            Alarm status of the object.
        """
        self.__alarm_status = alarm_status

    @property
    def alarm_status(self) -> AlarmStatus :
        """Gets the alarm status of the exception."""
        return self.__alarm_status