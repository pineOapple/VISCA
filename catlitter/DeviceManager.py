# -*- coding: utf-8 -*-
from __future__ import annotations
import coloredlogs
import verboselogs
from catlitter.CommandLoader import CommandLoader
from com.UARTCommunication import UARTCommunication
from dev.CameraHandler import CameraHandler

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

class DeviceManager:
    """
    Manages the creation and initialization of device handlers with their respective
    command loaders and communication interfaces.
    """

    def __init__(self, command_config, port, baudrate=9600):
        """
        Initializes the device manager with configurations for command loading and UART communication.

        Args:
            command_config (str): Path to the command configuration YAML file.
            port (str): The COM port for UART communication.
            baudrate (int): The baud rate for UART communication.
        """
        self.command_loader = CommandLoader(command_config)
        self.uart_communication = UARTCommunication(port=port, baudrate=baudrate)

    def get_camera_handler(self):
        """
        Creates and returns a CameraHandler initialized with the command loader and UART communication.

        Returns:
            CameraHandler: The initialized camera handler.
        """
        return CameraHandler(self.command_loader, self.uart_communication)
