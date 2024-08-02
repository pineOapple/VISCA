# -*- coding: utf-8 -*-
from __future__ import annotations
import typing as tp
import coloredlogs
import verboselogs
import yaml
import struct
import binascii
from catlitter.VirtualRegister import VirtualRegister

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
        commands (dict): Commands loaded from the YAML file.
        protocol (dict): Protocol configuration loaded from the YAML file.
    """

    def __init__(self, yaml_file: str):
        """
        Initialize the CommandLoader with the given YAML file.

        Args:
            yaml_file (str): Path to the YAML file containing commands.
        """
        logger.debug("Initializing CommandLoader with YAML file: %s", yaml_file)
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
            self.command_fields = data['COMMAND_FIELDS']
            self.protocol_fields = data['PROTOCOL_FIELDS']
        logger.debug("Loaded %d commands from YAML file", len(self.command_fields))

    def get_request_fields(self, name: str) -> tp.Optional[dict]:
        """
        Retrieve a command by name.

        Args:
            name (str): The name of the command to retrieve.

        Returns:
            dict: The command dictionary if found, otherwise None.
        """
        logger.debug("Searching for request fields from command: %s", name)
        request_fields = self.command_fields[name]['REQUEST']
        logger.debug("Fields found: %s", request_fields)
        return request_fields

    def get_response_fields(self, name: str) -> tp.Optional[dict]:
        """
        Retrieve a command by name.

        Args:
            name (str): The name of the command to retrieve.

        Returns:
            dict: The command dictionary if found, otherwise None.
        """
        logger.debug("Searching for repsonse fields from command: %s", name)
        response_fields = self.command_fields[name]['RESPONSE']
        logger.debug(str(len(response_fields)) + " Fields found: %s", response_fields)
        return response_fields

    def get_command_list(self):
        return list(self.command_fields.keys())

    def get_protocol(self) -> dict:
        """
        Retrieve the protocol configuration.

        Returns:
            dict: The protocol dictionary.
        """
        logger.debug("Protocol loaded: %s", self.protocol)
        return self.protocol_fields

    def get_command_dict(self, name):
        return self.command_fields[name]


class Field:
    """
    Represents a field with various attributes and functionalities.

    Attributes:
        name (str): The name of the field.
        load (int): The load value of the field.
        min (int): The minimum allowable load value.
        max (int): The maximum allowable load value.
        size (int): The size of the field.
        index (int): The index of the field.
        help_text (str): The help text associated with the field.
    """

    def __init__(self, name="", field_dict={}):
        """
        Initializes a Field instance.

        Args:
            name (str): The name of the field.
            field_dict (dict): A dictionary containing field attributes.
        """
        self.name = name
        self.load = field_dict.get('load')
        self.min = field_dict.get('min')
        self.max = field_dict.get('max')
        self.size = field_dict.get('size')
        self.index = field_dict.get('index')
        self.help_text = field_dict.get('help')
        self.value = 0
        if self.load:
            self.value = self.load[0]

    def set_load(self, value):
        """
        Sets the load value if within the allowable range.

        Args:
            value (int): The new load value.

        Raises:
            ValueError: If the value is outside the range (min, max).
        """
        if self.min and self.max:
            if self.min <= value <= self.max:
                self.value = value
                return
        self.value = value
        return
        raise ValueError(f"Value {value} out of range ({self.min}, {self.max})")

    def help(self):
        """
        Logs the help text of the field.
        """
        logger.debug(self.help_text)


class Command:
    def __init__(self):
        self.raw = None
        self.fields = {}
        self.next_index = 0
        self.help_text = None

    def add_field(self, name, field_dict):
        logger.debug("Adding Field: %s at index: " + str(self.next_index), name)
        self.fields[self.next_index] = Field(name, field_dict)
        self.next_index += 1
        self.update()
        # logger.debug("Added field %s successfully.", name)

    def set_parameter(self, name: str, value):
        for field in self.fields.values():
            if field.name == name:
                field.set_load(value)
                self.update()
                return
        raise ValueError(f"No field found with name {name}")

    def get_parameter(self, name):
        for field in self.fields.values():
            if field.name == name:
                return field.value
        raise ValueError(f"No field found with name {name}")

    def get_raw(self):
        self.update()
        return self.raw

    @staticmethod
    def crc16(data: bytes) -> int:
        """
        Compute CRC16 checksum.

        Args:
            data (bytes): The input data for which to compute the CRC16 checksum.

        Returns:
            int: The computed CRC16 checksum.
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
            crc &= 0xFFFF
        return crc

    def calculate_checksum(self, start_index: int, stop_index: int, target_index: int):
        """
        Calculates the CRC16 checksum for specified fields and sets it to the target field.

        Args:
            start_index (int): The start index of the fields to include in the checksum calculation.
            stop_index (int): The stop index of the fields to include in the checksum calculation.
            target_index (int): The index of the field where the checksum will be stored.

        Raises:
            ValueError: If any field has an invalid size or if indices are out of range.
        """
        if start_index < 0 or stop_index >= len(self.fields) or target_index >= len(self.fields):
            raise ValueError("Invalid indices")

        raw_data = b''
        for i in range(start_index, stop_index + 1):
            field = self.fields[i]
            if field.size == -1:
                raise ValueError(f"Field {field.name} has invalid size -1")

            size_in_bytes = (field.size + 7) // 8

            if field.load is None:
                field.value = 0

            field_data = field.value.to_bytes(size_in_bytes, byteorder='big')
            raw_data += field_data

        checksum = self.crc16(raw_data)
        self.fields[target_index].set_load(checksum)

    def update(self):

        raw_data = b''
        for field in self.fields.values():
            if field.size == -1:
                raise ValueError(f"Field {field.name} has invalid size -1")

            # Convert size from bits to bytes
            size_in_bytes = (field.size + 7) // 8

            if field.load is None:
                field.value = 0

            field_data = field.value.to_bytes(size_in_bytes, byteorder='big')
            raw_data += field_data

        self.raw = raw_data.hex()

    def __iter__(self) -> Field:
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index < len(self.fields):
            result = self.fields[self._iter_index]
            self._iter_index += 1
            return result
        else:
            raise StopIteration

    def __getitem__(self, item):
        for field in self.fields.values():
            if field.name == item:
                return field
        raise ValueError(f"No field found with name {name}")

    def help(self, name=None):
        if name:
            for field in self.fields.values():
                if field.name == name:
                    print(field.help_text)
                    return
            raise ValueError(f"No field found with name {name}")
        else:
            for field in self.fields.values():
                logger.debug(f"Help for Field {field.name}: {field.help_text}")


class CommandBuilder:
    def __init__(self, field_config: str):
        self.loader = CommandLoader(field_config)
        self.commands = self.loader.get_command_list()

    def build_command(self, cmd_name: str) -> Command:
        logger.debug("Building command %s...", cmd_name)

        command_dict = self.loader.get_command_dict(cmd_name)
        f_req_dict = command_dict['REQUEST']
        f_pro_dict = self.loader.protocol_fields

        cmd = Command()
        cmd.add_field('START_CHARACTER', f_pro_dict['START_CHARACTER'])
        cmd.add_field('COMMAND_ID', command_dict['COMMAND_ID'])
        cmd.add_field('PAYLOAD_SIZE', f_pro_dict['PAYLOAD_SIZE'])
        val = cmd['PAYLOAD_SIZE']
        val
        cmd.add_field('HEADER_CHECKSUM', f_pro_dict['HEADER_CHECKSUM'])
        # cmd.
        for key, value in f_req_dict.items():
            cmd.add_field(key, value)

        cmd.add_field('PAYLOAD_CHECKSUM', f_pro_dict['PAYLOAD_CHECKSUM'])
        cmd.calculate_checksum(0,2,3)
        # cmd.update()
        logger.debug("...built command %s", cmd_name)
        return cmd

    def build_response(self, response_name: str) -> Command:
        response_config = self.loader.get_command(response_name)

        if not response_config:
            logger.error(f"Response '{response_name}' not found")
            return None

        response = Command()
        response.fields = {key: Field(name=key, field_dict=value) for key, value in response_config.items() if
                           key != 'CMD_HELP'}
        logger.debug(f"Built response: {response}")

        return response

    def get_commands(self):
        return self.commands


# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

def main():
    loader = CommandLoader("../gimbal.yaml")
    logger.debug(loader.get_request_fields("CMD_BOARD_INFO"))
    logger.debug(loader.get_response_fields("CMD_BOARD_INFO"))
    logger.debug(loader.get_command_list())

    builder = CommandBuilder("../gimbal.yaml")
    logger.debug(builder.build_command('CMD_BOARD_INFO'))
    cmd = builder.build_command('CMD_BOARD_INFO')
    cmd.help()
    for field in cmd:
        logger.debug(field.name+'  :  '+str(field.value)+'  :  '+str(field.size))
    logger.debug(cmd.get_raw())
    logger.debug(cmd.get_parameter('CFG'))



if __name__ == "__main__":
    main()
