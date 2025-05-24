import types
import typing

import serial

class Port :
    """Port a pump is connected to."""

    BAUD_RATE_DEFAULT = 9_600
    """Default baud rate."""

    class Unavailability(Exception) :
        """Exception that indicates the unavailability of a port."""
        pass

    def __init__(self, name : str, baud_rate : int = BAUD_RATE_DEFAULT) -> None :
        """
        Constructs and opens a port.

        :param name:
            Name of the port.
        :param baud_rate:
            Baud rate at which data is exchanged via the port.

        :raises ValueError:
            Baud rate invalid.
        :raises Unavailability:
            Port unavailable (e.g. in use or not connected).
        """
        try :
            self.__serial = serial.Serial(
                port = name,
                baudrate = baud_rate
            )
        except ValueError :
            raise ValueError('Baud rate invalid.')
        except serial.SerialException :
            raise Port.Unavailability()

    def close(self) -> None :
        """Closes the port."""
        self.__serial.close()

    def __enter__(self) -> "Port" :
        return self

    def __exit__(
        self, type_ : typing.Optional[type[BaseException]], value : typing.Optional[BaseException],
        traceback : typing.Optional[types.TracebackType],
    ) -> None :
        self.close()

    def _transmit(self, data : bytes) -> None :
        """
        Transmits data to the port.

        :param data:
            Data to transmit.
        """
        self.__serial.write(data)

    def _receive(self, data_length : int) -> bytes :
        """
        Receives data from the port.

        :param data_length:
            Length of the data to receive.
        """
        return self.__serial.read(data_length)

    @property
    def _waiting_transmit(self) -> int :
        """Gets the length of data waiting to be transmitted."""
        return self.__serial.out_waiting

    @property
    def _waiting_receive(self) -> int :
        """Gets the length of data waiting to be received."""
        return self.__serial.in_waiting