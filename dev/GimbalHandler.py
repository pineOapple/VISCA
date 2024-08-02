# -*- coding: utf-8 -*-
from __future__ import annotations
import coloredlogs
import verboselogs

from catlitter import VirtualRegister, DeviceHandler

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
class GimbalHandler(DeviceHandler):
    def initialize_device(self):
        """
        Initialize the camera device with necessary startup commands.
        """
        logger.debug("Initializing gimbal device")
        self.execute_command('CAM_PowerOn')

    def help(self):
        """
        Extends the generic help to include camera-specific command information.
        """
        super().help()  # Call the base class help method
        # Add camera-specific commands or notes here if any

    def read_response(self) -> dict:
        """
        Read and interpret the VISCA response from the camera.
        Converts the response to a readable format and logs each part of the message.
        """
        response = self.communication_interface.read(10)  # Adjust size based on expected response length
        if not response:
            logger.debug("No response received.")
            return {"status": "error", "message": "No response received"}

        # Convert response to hexadecimal string
        readable_response = ''.join(f"{byte:02x}" for byte in response)
        logger.debug(f"Raw response received: {readable_response}")

        # Assuming messages are separated by 'ff' and start with '90'
        messages = readable_response.split('ff')
        for msg in messages:
            if msg.startswith('90'):
                self._evaluate_response(msg)

        return {"status": "completed", "message": "All messages processed"}

    def _evaluate_response(self, msg):
        """
        Evaluate a single VISCA message.
        """
        if msg[2:4] == '41':  # Example: '41' Acknowledgment
            logger.debug("[ACK] Acknowledgment received for a command.")
        elif msg[2:4] == '51':  # Example: '51' Command Completion
            logger.debug("[COMPLETION] Command completed successfully.")
        elif msg[2:4] == '60':  # Example: '60' Syntax Error
            logger.debug("[Syntax error] in command. Command format is incorrect or parameter value is out of range.")
        elif msg[2:4] == '61':  # Example: '61' Command Not Executable
            logger.debug("Command not executable. Current conditions do not allow this command to be executed.")
        else:
            logger.debug(f"Unknown VISCA message: {msg}")

    def execute_command(self, command_name: str, **kwargs):
        """
        Execute a command by name and evaluate the response using the VISCA protocol.
        Allows passing additional parameters as keyword arguments.

        Args:
            command_name (str): The name of the command to execute.
            **kwargs: Arbitrary keyword arguments representing command parameters.
        """
        command = self.command_loader.get_command(command_name)
        if command:
            if command_name not in self.registers:
                self.registers[command_name] = VirtualRegister(command)

            # Update command parameters with provided kwargs
            for param, value in kwargs.items():
                if param in self.registers[command_name].parameters:
                    self.registers[command_name].set_parameter(param, value)
                else:
                    logger.debug(f"Parameter {param} not recognized for command {command_name}")

            self.communication_interface.open()
            self.communication_interface.write(bytes(self.registers[command_name].get_bytes()))
            response = self.read_response()  # Use the specialized VISCA response reader
            self.communication_interface.close()
            logger.debug(f"Response for command '{command_name}': {response['message']}")
            if response['status'] == 'error':
                logger.debug(f"Error executing command '{command_name}': {response['message']}")
        else:
            logger.debug(f"Command '{command_name}' not found")

# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

def main():
    pass


if __name__ == "__main__":
    main()
