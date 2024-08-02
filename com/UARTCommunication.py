# -*- coding: utf-8 -*-
from __future__ import annotations
import coloredlogs
import verboselogs
import serial
from catlitter.CommunicationInterface import CommunicationInterface

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
logger = verboselogs.VerboseLogger(__name__)
coloredlogs.install(level="debug", logger=logger)


# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

def main():
    logger.warning("-------------------------------------")
    logger.warning("Performing unit test: UARTCommunication")
    logger.warning("-------------------------------------")
    com_if = UARTCommunication('COM13')

if __name__ == "__main__":
    main()
