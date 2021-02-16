import serial

class Port :
    """Port a pump is connected to."""

    # Default baud rate.
    BAUD_RATE_DEFAULT : int = 9600

    class Unavailability(Exception) :
        """Exception that indicates the unavailability of a port."""
        pass

    def __init__(self, name : str, baud_rate : int = BAUD_RATE_DEFAULT) -> None :
        """
        Constructs a port with the given name and baud rate.

        Raises ValueError if the baud rate is invalid with the port.
        Raises Unavailability if the port is unavailable.
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

    def transmit(self, data : bytes) -> None :
        """Transmits the given data to the port."""
        self.__serial.write(data)

    def receive(self, data_length : int) -> bytes :
        """Receives data of the given length from the port."""
        return self.__serial.read(data_length)

    @property
    def waiting_transmit(self) -> int :
        """Gets the length of data waiting to be transmitted."""
        return self.__serial.out_waiting

    @property
    def waiting_receive(self) -> int :
        """Gets the length of data waiting to be received."""
        return self.__serial.in_waiting