from .port import Port
from .status import Status
from .alarm import Alarm
from .pumping_direction import PumpingDirection
from .exceptions import *

import typing
import binascii
import re
import time

class Pump :
    """Pump."""

    # Default address.
    ADDRESS_DEFAULT = 0
    # Address limit.
    ADDRESS_LIMIT = 99

    # Default safe mode timeout in units of seconds.
    SAFE_MODE_TIMEOUT_DEFAULT = 0
    # Safe mode timeout limit in units of seconds.
    SAFE_MODE_TIMEOUT_LIMIT = 255

    # Minimum syringe diameter in units of millimeters.
    SYRINGE_DIAMETER_MINIMUM = 0.1
    # Maximum syringe diameter in units of millimeters.
    SYRINGE_DIAMETER_MAXIMUM = 80.0

    # Delay between pulling polls while waiting in units of seconds.
    PUMPING_POLL_DELAY = 0.05

    def __init__(
        self,
        port : Port,
        identity : int,
        address : int = ADDRESS_DEFAULT,
        safe_mode_timeout : int = SAFE_MODE_TIMEOUT_DEFAULT
    ) -> None :
        """
        Constructs a pump connected to the given port having the given identity, address, and safe
        mode timeout in units of seconds.
        """
        if address < 0 or address > Pump.ADDRESS_LIMIT :
            raise ValueError('Address invalid.')
        self.__port = port
        self.__address = address
        self.__safe_mode = True
        self.__safe_mode_timeout_set(safe_mode_timeout, True)
        identity_, firmware_version = self.__firmware_version_get()
        if identity_ != identity :
            raise ExceptionIdentity()
        self.__identity = identity_
        self.__firmware_version = firmware_version

    @property
    def address(self) -> int :
        """
        Gets the address of the pump.

        Values: [0, 'ADDRESS_LIMIT']
        """
        return self.__address

    @property
    def identity(self) -> int :
        """
        Gets the identity of the pump.

        Example: 1000 for NE-1000.
        """
        return self.__identity

    @property
    def firmware_version(self) -> typing.Tuple[int, int] :
        """Gets the firmware version of the pump as major version and minor version."""
        return self.__firmware_version

    @property
    def safe_mode_timeout(self) -> int :
        """Gets the safe mode timeout of the pump."""
        _, match = self.__command_transceive('SAF', [], Pump.__RE_PATTERN_SAFE_MODE_TIMEOUT)
        return int(match[1])

    @safe_mode_timeout.setter
    def safe_mode_timeout(self, safe_mode_timeout : int) -> None :
        """
        Sets the safe mode timeout of the pump.

        Values: [0, 'SAFE_MODE_TIMEOUT_LIMIT']

        A value of zero will set the communication to basic mode.
        A non-zero value will set the communication to safe mode.
        """
        self.__safe_mode_timeout_set(safe_mode_timeout, False)

    @property
    def status(self) -> Status :
        """Gets the status of the pump."""
        status, _ = self.__command_transceive('')
        return status

    @property
    def running(self) -> bool :
        """Gets if the pump is running."""
        return self.status in [Status.INFUSING, Status.WITHDRAWING, Status.PURGING]

    @property
    def syringe_diameter(self) -> float :
        """
        Gets the syringe diameter of the pump in units of millimeters.

        Values: [`SYRINGE_DIAMETER_MINIMUM`, `SYRINGE_DIAMETER_MAXIMUM`]
        """
        _, match = self.__command_transceive('DIA', [], Pump.__RE_PATTERN_SYRINGE_DIAMETER)
        return float(match[1])

    @syringe_diameter.setter
    def syringe_diameter(self, syringe_diameter : float) -> None :
        """
        Sets the syringe diameter of the pump in units of millimeters.

        Values: [`SYRINGE_DIAMETER_MINIMUM`, `SYRINGE_DIAMETER_MAXIMUM`]

        This value dictates the minimum and maximum pumping rate of the pump.

        Note: The value is truncated to the 4 most significant digits.
        """
        if (
            syringe_diameter < Pump.SYRINGE_DIAMETER_MINIMUM or
            syringe_diameter > Pump.SYRINGE_DIAMETER_MAXIMUM
        ) :
            raise ValueError('Syringe diameter invalid.')
        self.__command_transceive('DIA', [syringe_diameter])

    @property
    def pumping_direction(self) -> PumpingDirection :
        """Gets the pumping direction of the pump."""
        _, pumping_direction_string = self.__command_transceive('DIR')
        pumping_direction = Pump.__PUMPING_DIRECTION.get(pumping_direction_string)
        if pumping_direction is None :
            raise ExceptionInternal()
        return pumping_direction

    @pumping_direction.setter
    def pumping_direction(self, pumping_direction : PumpingDirection) -> None :
        """Sets the pumping direction of the pump."""
        pumping_direction_string = Pump.__PUMPING_DIRECTION_INTERNAL.get(pumping_direction)
        if pumping_direction_string is None :
            raise ValueError('Pumping direction invalid.')
        self.__command_transceive('DIR', [pumping_direction_string])

    @property
    def pumping_volume(self) -> float :
        """Gets the pumping volume of the pump in units of milliliters."""
        _, match = self.__command_transceive('VOL', [], Pump.__RE_PATTERN_PUMPING_VOLUME)
        value = float(match[1])
        units = match[2]
        value_milliliters = Pump.__VOLUME_MILLILITERS.get(units)
        if value_milliliters is None :
            raise ExceptionInternal()
        return value_milliliters(value)

    @pumping_volume.setter
    def pumping_volume(self, pumping_volume : float) -> None :
        """
        Sets the pumping volume of the pump in units of milliliters.

        Note: The value is truncated to the 4 most significant digits.
        """
        if pumping_volume < 0.001 / 1_000.0 or pumping_volume >= 10_000.0 :
            raise ValueError('Pumping rate invalid.')
        if pumping_volume >= 10_000.0 / 1_000.0 :
            units = 'ML'
        else :
            pumping_volume *= 1_000.0
            units = 'UL'
        self.__command_transceive('VOL', [units])
        try :
            self.__command_transceive('VOL', [pumping_volume])
        except ValueError :
            raise ValueError('Pumping volume invalid.')

    @property
    def pumping_rate(self) -> float :
        """Gets the pumping rate of the pump in units milliliters per minute."""
        _, match = self.__command_transceive('RAT', [], Pump.__RE_PATTERN_PUMPING_RATE)
        value = float(match[1])
        units = match[2]
        value_milliliters_per_minute = Pump.__PUMPING_RATE_MILLILITERS_PER_MINUTE.get(units)
        if value_milliliters_per_minute is None :
            raise ExceptionInternal()
        return value_milliliters_per_minute(value)

    @pumping_rate.setter
    def pumping_rate(self, pumping_rate : float) -> None :
        """
        Sets the pumping rate of the pump in units of milliliters per minute.

        The limits are dictated by the syringe diameter of the pump.

        Note: The value is truncated to the 4 most significant digits.
        """
        if pumping_rate < 0.001 / 60_000.0 or pumping_rate >= 10_000.0 :
            raise ValueError('Pumping rate invalid.')
        if pumping_rate >= 10_000.0 / 60.0 :
            units = 'MM'
        elif pumping_rate >= 10_000.0 / 1_000.0 :
            pumping_rate *= 60.0
            units = 'MH'
        elif pumping_rate >= 10_000.0 / 60_000.0 :
            pumping_rate *= 1_000.0
            units = 'UM'
        else :
            pumping_rate *= 60_000.0
            units = 'UH'
        try :
            self.__command_transceive('RAT', [pumping_rate, units])
        except ValueError :
            raise ValueError('Pumping rate invalid.')

    @property
    def volume_infused(self) -> int :
        """Gets the volume infused of the pump in units of milliliters."""
        return self.__dispensation_get(False)

    def volume_infused_clear(self) -> None :
        """Sets the volume infused of the pump to zero."""
        self.__command_transceive('CLD', ['INF'])

    @property
    def volume_withdrawn(self) -> int :
        """Gets the volume withdrawn of the pump in units of milliliters."""
        return self.__dispensation_get(True)

    def volume_withdrawn_clear(self) -> None :
        """Sets the volume withdrawn of the pump to zero."""
        self.__command_transceive('CLD', ['WDR'])

    def run(self, wait_while_running : bool = True) -> None :
        """Runs the pump considering the direction, volume, and rate set."""
        self.__command_transceive('RUN')
        if wait_while_running :
            self.wait_while_running()

    def run_purge(self) -> None :
        """
        Runs the pump considering the direction set at maximum rate.

        Running will continue until stopped.
        """
        self.__command_transceive('PUR')

    def stop(self) -> None :
        """Stops the pump."""
        self.__command_transceive('STP')

    def wait_while_running(self) -> None :
        """Waits while the pump is running."""
        while self.running :
            time.sleep(Pump.PUMPING_POLL_DELAY)

    # Start transmission
    __STX = 0x02
    # End transmission
    __ETX = 0x03

    __STATUS = {
        'I' : Status.INFUSING,
        'W' : Status.WITHDRAWING,
        'X' : Status.PURGING,
        'S' : Status.STOPPED,
        'P' : Status.PAUSED,
        'T' : Status.SLEEPING,
        'U' : Status.WAITING
    }

    __STATUS_ALARM = 'A'

    __ALARM = {
        'R' : Alarm.RESET,
        'S' : Alarm.STALLED,
        'T' : Alarm.TIMEOUT,
        'E' : Alarm.ERROR,
        'O' : Alarm.RANGE
    }

    # Regular expressions.
    __RE_INTEGER = r'(\d+)'
    __RE_FLOAT = r'(\d+\.\d*)'
    __RE_SYMBOL = '([A-Z]+)'

    # Format: "NE" <Identity> "V" <Firmware major version> "." <Firmware minor version>
    __RE_PATTERN_FIRMWARE_VERSION = re.compile(
        'NE' + __RE_INTEGER + 'V' + __RE_INTEGER + r'\.' + __RE_INTEGER, re.ASCII
    )
    __RE_PATTERN_SAFE_MODE_TIMEOUT = re.compile(__RE_INTEGER, re.ASCII)
    __RE_PATTERN_SYRINGE_DIAMETER = re.compile(__RE_FLOAT, re.ASCII)
    # Format: <Pumping volume> <Units>
    __RE_PATTERN_PUMPING_VOLUME = re.compile(__RE_FLOAT + __RE_SYMBOL, re.ASCII)
    # Format: <Pumping rate> <Units>
    __RE_PATTERN_PUMPING_RATE = re.compile(__RE_FLOAT + __RE_SYMBOL, re.ASCII)
    # Format: "I" <Volume infused> "W" <Volume withdrawn> <Units>
    __RE_PATTERN_DISPENSATION = re.compile('I' + __RE_FLOAT + 'W' + __RE_FLOAT + __RE_SYMBOL)

    __PUMPING_DIRECTION = {
        'INF' : PumpingDirection.INFUSE,
        'WDR' : PumpingDirection.WITHDRAW
    }

    __PUMPING_DIRECTION_INTERNAL = {
        PumpingDirection.INFUSE   : 'INF',
        PumpingDirection.WITHDRAW : 'WDR'
    }

    __PUMPING_RATE_MILLILITERS_PER_MINUTE = {
        # Milliliters per minute.
        'MM' : lambda value : value,
        # Milliliters per hour.
        'MH' : lambda value : value / 60.0,
        # Microliters per minute.
        'UM' : lambda value : value / 1_000.0,
        # Microliters per hour.
        'UH' : lambda value : value / 60_000.0,
    }

    __VOLUME_MILLILITERS = {
        # Milliliters.
        'ML' : lambda value : value,
        # Microliters.
        'UL' : lambda value : value / 1_000.0,
    }

    __VOLUME_MILLILITERS_SET = {
        # Milliliters.
        'ML' : lambda value : value,
        # Microliters.
        'UL' : lambda value : value * 1_000.0,
    }

    __ERROR = {
        # Not applicable.
        'NA'  : lambda : Pump.__error_handle_not_applicable(),
        # Out of range.
        'OOR' : lambda : Pump.__error_handle_out_of_range(),
        # Communication.
        'COM' : lambda : Pump.__error_handle_communication(),
        # Ignored.
        'IGN' : lambda : Pump.__error_handle_ignored()
    }

    __ARGUMENT = {
        str   : lambda value : Pump.__argument_str(value),
        int   : lambda value : Pump.__argument_int(value),
        float : lambda value : Pump.__argument_float(value)
    }

    @staticmethod
    def __error_handle_not_applicable() -> None :
        raise ExceptionState()

    @staticmethod
    def __error_handle_out_of_range() -> None :
        raise ValueError()

    @staticmethod
    def __error_handle_communication() -> None :
        raise ExceptionChecksumRequest()

    @staticmethod
    def __error_handle_ignored() -> None :
        pass

    @staticmethod
    def __argument_str(value : str) -> str :
        return value

    @staticmethod
    def __argument_int(value : int) -> str :
        return str(value)

    @staticmethod
    def __argument_float(value : float) -> str :
        # From the docs: Maximum of 4 digits plus 1 decimal point. Maximum of 3 digits to the right
        # of the decimal point.
        if value.is_integer() :
            return str(int(value))
        value_string = str(value)
        if len(value_string) > 5 :
            value_string = value_string[0 : 5]
        return value_string

    @staticmethod
    def __command_checksum_calculate(data : bytes) -> int :
        """Gets the CCITT-CRC of the given data."""
        return binascii.crc_hqx(data, 0x0000)

    @staticmethod
    def __command_request_format(
        address : int,
        name : str,
        arguments : typing.Iterable[typing.Union[str, int, float]] = []
    ) -> str :
        return str(address) + name + ''.join(
            Pump.__ARGUMENT[type(argument)](argument)
            for argument in arguments
        )

    @classmethod
    def __command_reply_parse(
        cls,
        address : int,
        data_string : str
    ) -> typing.Tuple[Status, typing.Optional[Alarm], str] :
        data_length = len(data_string)
        if data_length < 3 :
            raise ExceptionInternal()
        address_string = data_string[0 : 2]
        address_ = int(address_string)
        if address_ != address :
            raise ExceptionInternal()
        status_string = data_string[2]
        if status_string == cls.__STATUS_ALARM :
            if data_string[3] != '?' :
                raise ExceptionInternal()
            alarm_string = data_string[4]
            alarm = cls.__ALARM.get(alarm_string)
            if alarm is None :
                raise ExceptionInternal()
            return Status.STOPPED, alarm, ''
        status = cls.__STATUS.get(status_string)
        if status is None :
            raise ExceptionInternal()
        result = data_string[3 : data_length]
        if result and result[0] == '?' :
            error_string = result[1 :]
            error = cls.__ERROR.get(error_string)
            if error is None :
                raise ExceptionInternal()
            error()
        return status, None, result

    @classmethod
    def __command_request_transmit_port_basic(
        cls,
        port : Port,
        address : int,
        name : str,
        arguments : typing.Iterable[typing.Union[str, int, float]] = []
    ) -> None :
        data_string = cls.__command_request_format(address, name, arguments) + '\r'
        port.transmit(data_string.encode())

    @classmethod
    def __command_request_transmit_port_safe(
        cls,
        port : Port,
        address : int,
        name : str,
        arguments : typing.Iterable[typing.Union[str, int, float]] = []
    ) -> None :
        data_string = cls.__command_request_format(address, name, arguments)
        data = data_string.encode()
        checksum = cls.__command_checksum_calculate(data)
        data = [
            cls.__STX,
            # Length (1 byte) + Checksum (2 bytes) + ETX (1 byte) = 4 bytes
            len(data) + 4,
            *data,
            *checksum.to_bytes(2, byteorder = 'big', signed = False),
            cls.__ETX
        ]
        port.transmit(bytes(data))

    @classmethod
    def __command_reply_receive_port_basic(
        cls,
        port : Port,
        address : int
    ) -> typing.Tuple[Status, typing.Optional[Alarm], str] :
        data = port.receive(1)
        if data[0] != cls.__STX :
            raise ExceptionInternal()
        data = bytearray()
        while True :
            data_length = max(1, port.waiting_receive)
            data.extend(port.receive(data_length))
            if data[-1] == cls.__ETX :
                del data[-1]
                break
        data_string = data.decode()
        return cls.__command_reply_parse(address, data_string)

    @classmethod
    def __command_reply_receive_port_safe(
        cls,
        port : Port,
        address : int
    ) -> typing.Tuple[Status, typing.Optional[Alarm], str] :
        data_header = port.receive(2)
        if data_header[0] != cls.__STX :
            raise ExceptionInternal()
        data_length = data_header[1]
        if data_length <= 2 :
            raise ExceptionInternal()
        data = port.receive(data_length - 1)
        if data[-1] != cls.__ETX :
            raise ExceptionInternal()
        checksum = int.from_bytes(data[-3 : -1], byteorder = 'big', signed = False)
        data = data[0 : -3]
        if checksum != cls.__command_checksum_calculate(data) :
            raise ExceptionChecksumReply()
        data_string = data.decode()
        return cls.__command_reply_parse(address, data_string)

    @classmethod
    def __command_transceive_port(
        cls,
        port : Port,
        safe_mode : bool,
        address : int,
        name : str,
        arguments : typing.Iterable[typing.Union[str, int, float]] = [],
        re_pattern_result : typing.Optional[re.Pattern] = None,
        alarm_ignore : bool = False,
        safe_mode_receive : typing.Optional[int] = None
    ) -> typing.Tuple[Status, typing.Union[str, re.Match]] :
        if safe_mode_receive is None :
            safe_mode_receive = safe_mode
        while True :
            if safe_mode :
                cls.__command_request_transmit_port_safe(port, address, name, arguments)
            else :
                cls.__command_request_transmit_port_basic(port, address, name, arguments)
            if safe_mode_receive :
                status, alarm, result = cls.__command_reply_receive_port_safe(port, address)
            else :
                status, alarm, result = cls.__command_reply_receive_port_basic(port, address)
            if alarm is not None and alarm_ignore :
                alarm_ignore = False
            else :
                break
        if alarm is not None :
            raise ExceptionStatusAlarm(alarm)
        if re_pattern_result is None :
            return status, result
        match = re_pattern_result.fullmatch(result)
        if match is None :
            raise ExceptionInternal()
        return status, match

    def __command_transceive(
        self,
        name : str,
        arguments : typing.Iterable[typing.Union[str, int, float]] = [],
        re_pattern_result : typing.Optional[re.Pattern] = None,
        alarm_ignore : bool = False,
        safe_mode_receive : typing.Optional[bool] = None
    ) -> typing.Tuple[Status, typing.Union[str, re.Match]] :
        reply = Pump.__command_transceive_port(
            self.__port,
            self.__safe_mode,
            self.__address,
            name,
            arguments,
            re_pattern_result,
            alarm_ignore,
            safe_mode_receive
        )
        if safe_mode_receive is not None :
            self.__safe_mode = safe_mode_receive
        return reply

    def __safe_mode_timeout_set(self, safe_mode_timeout : int, alarm_ignore : bool) -> None :
        if safe_mode_timeout < 0 or safe_mode_timeout > Pump.SAFE_MODE_TIMEOUT_LIMIT :
            raise ValueError('Safe mode timeout invalid.')
        safe_mode = safe_mode_timeout != 0
        self.__command_transceive(
            'SAF', [safe_mode_timeout], alarm_ignore = alarm_ignore, safe_mode_receive = safe_mode
        )
        self.__safe_mode = safe_mode

    def __firmware_version_get(self) -> typing.Tuple[int, typing.Tuple[int, int]] :
        _, match = self.__command_transceive(
            'VER', [], Pump.__RE_PATTERN_FIRMWARE_VERSION
        )
        identity = int(match[1])
        firmware_major_version = int(match[2])
        firmware_minor_version = int(match[3])
        return identity, (firmware_major_version, firmware_minor_version)

    def __dispensation_get(self, withdrawn : bool) -> float :
        _, match = self.__command_transceive('DIS', [], Pump.__RE_PATTERN_DISPENSATION)
        value = float(match[1 + withdrawn])
        units = match[3]
        value_milliliters = Pump.__VOLUME_MILLILITERS.get(units)
        if value_milliliters is None :
            raise ExceptionInternal()
        return value_milliliters(value)