# -*- coding: utf-8 -*-
from __future__ import annotations
import coloredlogs
import verboselogs

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
        logger.debug("Initializing VirtualRegister with command: %s", command)
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
                logger.debug("Cannot set value directly for a parameter byte at index %d", index)
                raise ValueError("Cannot set value directly for a parameter byte")
            self.bytes[index] = value
            logger.debug("Byte set successfully at index %d", index)
        else:
            logger.debug("Byte index %d out of range", index)
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
        TODO: move to DeviceHandlerBase
        Get the possible parameters for the command.

        Returns:
            dict: Dictionary of parameters and their possible values.
        """
        logger.debug("Getting possible parameters: %s", self.parameters)
        return self.parameters

    def set_parameter(self, param: str, value: int):
        """
        TODO: move to DeviceHandlerBase
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
                logger.debug("Value %02X not valid for parameter %s", value, param)
                raise ValueError(f"Value {value} not valid for parameter {param}")
        else:
            logger.debug("Parameter %s not valid for this command", param)
            raise ValueError(f"Parameter {param} not valid for this command")





# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

def main():
    pass


if __name__ == "__main__":
    main()
