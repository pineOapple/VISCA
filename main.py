# -*- coding: utf-8 -*-
from __future__ import annotations
import coloredlogs
import verboselogs
from catlitter.DeviceManager import DeviceManager
# import catlitter
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






# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

def main():
    device_manager = DeviceManager(command_config='commands.yaml', port='COM9', baudrate=9600)
    camera_handler = device_manager.get_camera_handler()
    camera_handler.initialize_device()
    camera_handler.execute_command('CAM_ZoomTeleVariable', speed=2)


if __name__ == "__main__":
    main()
