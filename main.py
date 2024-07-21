from __future__ import annotations
from abc import ABC, abstractmethod
import typing as tp
import coloredlogs
import verboselogs
import serial
import time
import yaml

# -----------------------------------------------------------------------------
# COPYRIGHT
# -----------------------------------------------------------------------------

__author__ = "Noel Ernsting Luz"
__copyright__ = "Copyright (C) 2022 Noel Ernsting Luz"
__license__ = "Public Domain"
__version__ = "1.0"

# -----------------------------------------------------------------------------
# LOGGER
# -----------------------------------------------------------------------------

verboselogs.install()
logger = verboselogs.VerboseLogger("module_logger")
coloredlogs.install(level="debug", logger=logger)


# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class CommandLoader:
    """
    Class to load and manage commands from a YAML file.

    Attributes:
        commands (list): List of commands loaded from the YAML file.
    """

    def __init__(self, yaml_file: str):
        """
        Initialize the CommandLoader with the given YAML file.

        Args:
            yaml_file (str): Path to the YAML file containing commands.
        """
        logger.verbose("Initializing CommandLoader with YAML file: %s", yaml_file)
        with open(yaml_file, 'r') as file:
            self.commands = yaml.safe_load(file)['commands']
        logger.verbose("Loaded %d commands from YAML file", len(self.commands))

    def get_command(self, name: str) -> tp.Optional[dict]:
        """
        Retrieve a command by name.

        Args:
            name (str): The name of the command to retrieve.

        Returns:
            dict: The command dictionary if found, otherwise None.
        """
        logger.debug("Searching for command with name: %s", name)
        for command in self.commands:
            if command['name'] == name:
                logger.debug("Command found: %s", command)
                return command
        logger.verbose("Command not found: %s", name)
        return None


class VirtualRegister:
    """
    Class to represent a virtual register for managing command bytes and parameters.

    Attributes:
        command (dict): The command dictionary.
        bytes (list): List of command bytes.
        parameters (dict): Dictionary of parameters and their possible values.
    """

    def __init__(self, command: dict):
        """
        Initialize the VirtualRegister with the given command.

        Args:
            command (dict): The command dictionary.
        """
        logger.verbose("Initializing VirtualRegister with command: %s", command)
        self.command = command
        self.bytes = command['bytes']
        self.parameters = self._extract_parameters()
        logger.debug("Extracted parameters: %s", self.parameters)

    def _extract_parameters(self) -> dict:
        """
        Extract parameters from the command bytes.

        Returns:
            dict: Dictionary of parameters and their possible values.
        """
        logger.debug("Extracting parameters from command bytes")
        parameters = {}
        for byte in self.bytes:
            if isinstance(byte, dict):
                parameters[byte['param_name']] = byte['values']
        logger.debug("Parameters extracted: %s", parameters)
        return parameters

    def set_byte(self, index: int, value: int):
        """
        Set a specific byte in the command bytes.

        Args:
            index (int): The index of the byte to set.
            value (int): The value to set the byte to.

        Raises:
            ValueError: If trying to set a value directly for a parameter byte.
            IndexError: If the byte index is out of range.
        """
        logger.debug("Setting byte at index %d to value %02X", index, value)
        if index < len(self.bytes):
            if isinstance(self.bytes[index], dict):
                logger.error("Cannot set value directly for a parameter byte at index %d", index)
                raise ValueError("Cannot set value directly for a parameter byte")
            self.bytes[index] = value
            logger.debug("Byte set successfully at index %d", index)
        else:
            logger.error("Byte index %d out of range", index)
            raise IndexError("Byte index out of range")

    def get_bytes(self) -> list[int]:
        """
        Retrieve the current command bytes.

        Returns:
            list[int]: List of current command bytes.
        """
        logger.debug("Retrieving command bytes")
        byte_array = [byte if not isinstance(byte, dict) else 0x00 for byte in self.bytes]
        logger.debug("Current command bytes: %s", byte_array)
        return byte_array

    def get_possible_parameters(self) -> dict:
        """
        Get the possible parameters for the command.

        Returns:
            dict: Dictionary of parameters and their possible values.
        """
        logger.debug("Getting possible parameters: %s", self.parameters)
        return self.parameters

    def set_parameter(self, param: str, value: int):
        """
        Set a specific parameter value in the command bytes.

        Args:
            param (str): The parameter name to set.
            value (int): The value to set the parameter to.

        Raises:
            ValueError: If the parameter is not valid for this command or the value is not valid for the parameter.
        """
        logger.debug("Setting parameter %s to value %02X", param, value)
        if param in self.parameters:
            if value in self.parameters[param]:
                for i, byte in enumerate(self.bytes):
                    if isinstance(byte, dict) and byte['param_name'] == param:
                        self.bytes[i] = value
                        logger.debug("Parameter %s set to value %02X at index %d", param, value, i)
                        break
            else:
                logger.error("Value %02X not valid for parameter %s", value, param)
                raise ValueError(f"Value {value} not valid for parameter {param}")
        else:
            logger.error("Parameter %s not valid for this command", param)
            raise ValueError(f"Parameter {param} not valid for this command")


class CommunicationInterface(ABC):
    """
    Abstract base class for hardware communication interfaces.

    Subclasses should implement methods for opening, closing, reading from,
    and writing to the communication interface.
    """

    @abstractmethod
    def open(self):
        """
        Open the communication interface.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close the communication interface.
        """
        pass

    @abstractmethod
    def read(self, size: int) -> bytes:
        """
        Read data from the communication interface.

        Args:
            size (int): The number of bytes to read.

        Returns:
            bytes: The data read from the communication interface.
        """
        pass

    @abstractmethod
    def write(self, data: bytes):
        """
        Write data to the communication interface.

        Args:
            data (bytes): The data to write.
        """
        pass


class UARTCommunication(CommunicationInterface):
    """
    UART communication interface implementation.

    Attributes:
        port (str): The UART port to use.
        baudrate (int): The baud rate for UART communication.
        timeout (float): The read timeout for UART communication.
        ser (serial.Serial): The serial communication object.
    """

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        """
        Initialize the UARTCommunication with the given parameters.

        Args:
            port (str): The UART port to use.
            baudrate (int): The baud rate for UART communication.
            timeout (float): The read timeout for UART communication.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def open(self):
        """
        Open the UART communication interface.
        """
        logger.debug("Opening UART port: %s", self.port)
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        logger.debug("UART port opened: %s", self.port)

    def close(self):
        """
        Close the UART communication interface.
        """
        logger.debug("Closing UART port: %s", self.port)
        if self.ser and self.ser.is_open:
            self.ser.close()
            logger.debug("UART port closed: %s", self.port)

    def read(self, size: int) -> bytes:
        """
        Read data from the UART communication interface.

        Args:
            size (int): The number of bytes to read.

        Returns:
            bytes: The data read from the UART communication interface.
        """
        logger.debug("Reading %d bytes from UART port: %s", size, self.port)
        data = self.ser.read(size)
        logger.debug("Read data: %s", data)
        return data

    def write(self, data: bytes):
        """
        Write data to the UART communication interface.

        Args:
            data (bytes): The data to write.
        """
        logger.debug("Writing data to UART port: %s", self.port)
        self.ser.write(data)
        logger.debug("Data written to UART port: %s", data)


class DeviceHandler(ABC):
    def __init__(self, command_loader: CommandLoader, communication_interface: CommunicationInterface):
        self.command_loader = command_loader
        self.communication_interface = communication_interface
        self.registers = {}

    @abstractmethod
    def initialize_device(self):
        """
        Initialize the device with necessary startup commands.
        """
        pass

    def execute_command(self, command_name: str):
        """
        Execute a command by name.

        Args:
            command_name (str): The name of the command to execute.
        """
        command = self.command_loader.get_command(command_name)
        if command:
            if command_name not in self.registers:
                self.registers[command_name] = VirtualRegister(command)
            self.communication_interface.open()
            self.communication_interface.write(bytes(self.registers[command_name].get_bytes()))
            response = self.communication_interface.read(10)
            self.communication_interface.close()
            logger.info(f"Executed command '{command_name}': Response: {response}")
        else:
            logger.error(f"Command '{command_name}' not found")

    def help(self):
        """
        Displays help information for all available commands and their parameters.
        """
        logger.info("Available Commands:")
        for cmd in self.command_loader.commands:
            logger.info(f"Command: {cmd['name']}")
            logger.info(f"  Description: {cmd['description']}")
            if 'parameters' in cmd:
                logger.info("  Parameters:")
                for param, details in cmd['parameters'].items():
                    logger.info(f"    {param}: {details['description']}")


class CameraHandler(DeviceHandler):
    def initialize_device(self):
        """
        Initialize the camera device with necessary startup commands.
        """
        logger.info("Initializing camera device")
        self.execute_command('CAM_PowerOn')

    def turn_off(self):
        """
        Turn off the camera.
        """
        logger.info("Turning off the camera")
        self.execute_command('CAM_PowerOff')

    def help(self):
        """
        Extends the generic help to include camera-specific command information.
        """
        super().help()  # Call the base class help method
        logger.info("Camera-specific commands:")
        # Add camera-specific commands or notes here if any


# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

def main():
    logger.info("Starting main function")
    command_loader = CommandLoader('commands.yaml')
    uart_communication = UARTCommunication(port='/dev/ttyUSB0', baudrate=9600)
    camera_handler = CameraHandler(command_loader, uart_communication)

    # Display help information
    camera_handler.help()

    # Initialize the camera
    camera_handler.initialize_device()


if __name__ == "__main__":
    main()
