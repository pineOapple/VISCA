# -*- coding: utf-8 -*-
from __future__ import annotations
import coloredlogs
import verboselogs
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
# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

def main():
    pass


if __name__ == "__main__":
    main()
