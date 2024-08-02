# -*- coding: utf-8 -*-
from __future__ import annotations
import coloredlogs
import verboselogs
from catlitter import CommandLoader
from catlitter import CommunicationInterface
from abc import ABC, abstractmethod

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

    @abstractmethod
    def execute_command(self, command_name: str):
        """
        Execute a command by name.

        Args:
            command_name (str): The name of the command to execute.
        """
        raise NotImplemented


    def help(self):
        """
        Displays help information for all available commands and their parameters.
        """
        logger.debug("Available Commands:")
        for cmd in self.command_loader.commands:
            logger.debug(f"Command: {cmd['name']}")
            logger.debug(f"  Description: {cmd['description']}")
            if 'parameters' in cmd:
                logger.debug("  Parameters:")
                for param, details in cmd['parameters'].items():
                    logger.debug(f"    {param}: {details['description']}")
# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

def main():
    pass


if __name__ == "__main__":
    main()
