# -*- coding: utf-8 -*-
from __future__ import annotations
import coloredlogs
import verboselogs
import crcmod
import struct
import typing as tp
from abc import ABC, abstractmethod
import yaml
from bitstring import Bits, BitArray
import struct
import binascii
# -----------------------------------------------------------------------------
# COPYRIGHT
# -----------------------------------------------------------------------------

__author__ = "Noel Ernsting Luz"
__copyright__ = "Copyright (C) 2024 Noel Ernsting Luz"
__license__ = "Public Domain"
__version__ = "1.0"

# -----------------------------------------------------------------------------
# LOGGER
# -----------------------------------------------------------------------------

verboselogs.install()
logger = verboselogs.VerboseLogger(__name__)
coloredlogs.install(level="verbose", logger=logger)


# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class CommandLoader:
    def __init__(self, yaml_file: str) -> None:
        logger.debug("Initializing CommandLoader with YAML file: %s", yaml_file)
        with open(yaml_file, 'r') as file:
            self.data = yaml.safe_load(file)
        logger.debug("Loaded %d fieldgroups from YAML file", len(self.data))

    def get_commands(self) -> list:
        logger.debug("Searching for available commands...")
        results = list(self.data['COMMAND_FIELDS'].keys())
        logger.debug("%s commands found...", len(results))
        return results

    def get_command_dict(self, name) -> dict:
        logger.debug("Searching command dict for "+name)
        if name in self.get_commands():
            logger.debug("Command dict found!")
            return self.data['COMMAND_FIELDS'][name]
        logger.error("Command not found.")

    def get_protocol_dict(self) -> dict:
        logger.debug("Searching for additional fields...")
        results = self.data['PROTOCOL_FIELDS']
        if results:
            logger.debug("Additional fields found!")
            return results

    def get_request_dict(self, name) -> dict:
        logger.debug("Searching request dict for "+name)
        result = self.get_command_dict(name)
        result = result['REQUEST']
        logger.debug("Found request fields!")
        return result

    def get_response_dict(self, name):
        logger.debug("Searching response dict for "+name)
        logger.debug("")

    def load(self, yaml_file: str) -> None:
        logger.debug("Reinitializing CommandLoader with YAML file: %s", yaml_file)
        with open(yaml_file, 'r') as file:
            self.data = yaml.safe_load(file)
        logger.debug("Loaded %d fieldgroups from YAML file", len(self.data))

class Field:
    def __init__(self, name, load=None, min=None, max=None, size=8, help_str=None, value=0, **kwargs) -> None:
        logger.debug("Initializing field %s ...", name)
        self.name = name
        self.value = value
        self.load = load
        self.min = min
        self.max = max
        self.size = size
        self.help_str = help_str
        if load:
            self.set_val(load[0])

        logger.debug("Initialized Field %s", self.name)
        logger.spam("Set field load to %s", self.load)
        logger.spam("Set field min to %s", self.min)
        logger.spam("Set field max to %s", self.max)
        logger.spam("Set field size to %s", self.size)
        logger.spam("Set field help_str to %s", self.help_str)
        logger.spam("Set field value to %s", self.value)

    def get_name(self) -> str:
        logger.debug("Fetching name...")
        result = self.name
        logger.debug("name found! %s", result)
        return result

    def get_load(self) -> list:
        logger.debug("Fetching load (defaults)...")
        result = self.load
        logger.debug("load (defaults) found! %s", result)
        return result

    def get_min(self) -> int:
        logger.debug("Fetching min...")
        result = self.min
        logger.debug("min found! %s", result)
        return result

    def get_max(self) -> int:
        logger.debug("Fetching max...")
        result = self.max
        logger.debug("max found! %s", result)
        return result

    def set_val(self, value: int) -> None:
        if self.min:
            assert value >= self.min, "Error while trying to set value. Did you check min?"

        if self.max:
            assert value <= self.max, "Error while trying to set value. Did you check max?"

        if self.load:
            try:
                assert value in self.load, "Error while trying to set value. Did you check load?"
            except:
                logger.error("Error while trying to set parameter %s", self.name)
                logger.error("Select one of the following values: %s", self.load)

        if isinstance(value,int):
            self.value = value
            logger.debug("Setting value to %s of field "+self.name, value)
            return

        logger.error("Unknown error while trying to set value")

    def get_val(self) -> int:
        logger.debug("Fetching value...")
        result = self.value
        logger.debug("Value found! %s", result)
        return result

    def get_raw(self) -> Bits:
        bits = Bits(uint=self.value, length=self.size)
        return bits

    def help(self) -> None:
        logger.info(self.help_str)
        return self.help_str

    def __repr__(self):
        return self.name


class Command:
    def __init__(self, name, help_str):
        logger.debug("Initializing command %s ...", name)
        self.name = name
        self.fields = {}
        self.help_str = help_str
        self.next_index = 0
        logger.debug("Initialized command %s", name)

    def get_parameters(self) -> list:
        logger.debug("Searching available parameters...")
        results = []
        for field in self:
            results.append(field.get_name())
        if results:
            logger.debug("Parameters found! %s", results)
            return results

    def add_field(self, field: Field) -> None:
        logger.debug("Adding field at index %s", self.next_index)

        self.fields[self.next_index] = field
        self.next_index += 1
        logger.debug("Added field.")

    def get_field(self, name=None, index=None) -> Field:
        if index:
            return self.fields[index]
        if name:
            for field in self:
                if field.get_name() == name:
                    return field
        logger.error("Neither name nor index given. Please set either.")

    def set_field(self, name, value) -> None:
        logger.debug("")
        self.get_field(name=name).set_val(value)
        logger.debug("")

    def get_size(self) -> int:
        logger.debug("")
        size = 0
        for field in self:
            size+=field.size
        return size

    def get_name(self) -> str:
        logger.debug("")
        return self.name

    def get_raw(self, start_index = 0, end_index=None) -> bytes:

        assert len(self) > 0, "Add some fields first."
        if not end_index:
            end_index = len(self)

        fields = [field for field in self]
        fields = fields[start_index:end_index+1]
        result = b''

        for field in fields:
            result += field.get_raw()

        if isinstance(result, Bits):
            result = result.tobytes()
            return result

        raise ValueError

    def __iter__(self) -> Command:
        logger.spam("Initialized iteration.")
        self._iter_index = 0
        logger.spam("Iteration initialized.")
        return self

    def __next__(self):
        logger.spam("Current index in iteration: %s", self._iter_index)
        if self._iter_index < len(self.fields):
            result = self.fields[self._iter_index]
            self._iter_index += 1
            return result
        else:
            raise StopIteration

    def __len__(self):
        return self.next_index

    def __getitem__(self, item):
        return self.get_field(item)

    def help(self) -> str:
        logger.info(self.help_str)
        return self.help_str

    # def crc16_calculate(length, data: bytes) -> bytes:

    def crc16_calculate(self, start_index, stop_index, target_index) -> bytes:
        # NO FUCKING CLUE HOW I GOT THAT WORKING
        fields_total = [field for field in self]
        fields = fields_total[start_index:stop_index + 1]
        size = 0
        for field in fields:
            size += field.size

        assert size % 8 == 0, "CRC only works for full bytes here."
        length = size // 8
        data = self.get_raw(start_index=start_index, end_index=stop_index)

        crc = [0, 0]
        polynom = 0x8005
        crc_register = (crc[0] & 0xFF) | ((crc[1] & 0xFF) << 8)

        for counter in range(length):
            for shift_register in range(8):
                data_bit = (data[counter] >> shift_register) & 0x01
                crc_bit = (crc_register >> 15) & 0x01
                crc_register <<= 1
                crc_register &= 0xFFFF  # Ensure CRC register remains 16-bit
                if data_bit != crc_bit:
                    crc_register ^= polynom
                crc_register &= 0xFFFF  # Ensure CRC register remains 16-bit

        crc[0] = crc_register & 0xFF
        crc[1] = (crc_register >> 8) & 0xFF
        target_field: Field = fields_total[target_index]
        self.set_field(target_field.name, int.from_bytes(bytes(crc), "big"))
        return bytes(True)



class CommandManager:
    def __init__(self, field_yaml):
        logger.debug("")
        logger.debug("")

    def build_command(self, name):
        logger.debug("")
        logger.debug("")

    def build_response(self, name):
        logger.debug("")
        logger.debug("")

    def get_commands(self):
        logger.debug("")
        logger.debug("")

    def get_command(self, name):
        logger.debug("")
        logger.debug("")

# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------




def main():
    # Unit test for Commandloader
    logger.warning("-------------------------------------")
    logger.warning("Performing unit test: CommandLoader:")
    logger.warning("-------------------------------------")
    loader = CommandLoader('gimbal.yaml')

    logger.info("Performing method test: get_commands:")
    logger.verbose(loader.get_commands())

    logger.info("Performing method test: get_commands:")
    logger.verbose(loader.get_command_dict('CMD_BOARD_INFO'))

    logger.info("Performing method test: get_protocol_dict:")
    logger.verbose(loader.get_protocol_dict())

    logger.info("Performing method test: get_request_dict:")
    logger.verbose(loader.get_request_dict('CMD_BOARD_INFO'))

    logger.info("Performing method test: get_response_dict:")
    logger.verbose(loader.get_response_dict('CMD_BOARD_INFO'))

    # Unit test for Field
    logger.warning("-------------------------------------")
    logger.warning("Performing unit test: Field")
    logger.warning("-------------------------------------")
    field1 = Field(load=[0x56, 0, 1, 3, 4],
                  min=None,
                  max=None,
                  size=13,
                  help_str="Helper string for EXAMPLE_FIELD",
                  name='EXAMPLE_FIELD1')
    field2 = Field(load=[0x56],
                  min=None,
                  max=None,
                  size=13,
                  help_str="Helper string for EXAMPLE_FIELD",
                  name='EXAMPLE_FIELD2')
    field3 = Field(load=[0x56],
                  min=None,
                  max=None,
                  size=13,
                  help_str="Helper string for EXAMPLE_FIELD",
                  name='EXAMPLE_FIELD3')

    logger.info("Performing method test: get_commands:")
    logger.verbose(field1.get_name())

    logger.info("Performing method test: get_load:")
    logger.verbose(field1.get_load())

    logger.info("Performing method test: get_max:")
    logger.verbose(field1.get_max())

    logger.info("Performing method test: get_min:")
    logger.verbose(field1.get_min())

    logger.info("Performing method test: get_val:")
    logger.verbose(field1.get_val())

    logger.info("Performing method test: set_val:")
    logger.verbose(field1.set_val(86))

    logger.info("Performing method test: get_val:")
    logger.verbose(field1.get_val())

    logger.info("Performing method test: get_raw:")
    logger.verbose(field1.get_raw())

    logger.info("Performing method test: help")
    logger.verbose(field1.help())

    # Unit test for Command
    logger.warning("-------------------------------------")
    logger.warning("Performing unit test: Command")
    logger.warning("-------------------------------------")
    cmd = Command("EXAMPLE_CMD", "Custom command for unit testing")

    logger.info("Performing method test: get_parameters:")
    logger.verbose(cmd.get_parameters())

    logger.info("Performing method test: add_field:")
    logger.verbose(cmd.add_field(field1))
    cmd.add_field(field2)
    cmd.add_field(field3)

    logger.info("Performing method test: get_field:")
    logger.verbose(cmd.get_field(name='EXAMPLE_FIELD1', index=0))

    logger.info("Performing method test: set_field:")
    logger.verbose(cmd.set_field("EXAMPLE_FIELD1", 0))

    logger.info("Performing method test: get_name:")
    logger.verbose(cmd.get_name())

    logger.info("Performing method test: get_raw:")
    logger.verbose(cmd.get_raw())

    logger.info("Performing method test: __iter__,__next__:")
    logger.verbose([field for field in cmd])

    logger.info("Performing method test: get_parameters:")
    logger.verbose(cmd.get_parameters())

    logger.warning("-------------------------------------")
    logger.warning("Performing cmd test: CMD_BOARD_INFO")
    logger.warning("-------------------------------------")
    cmd = Command("CMD_BOARD_INFO", "Simple format: no parameters")
    f1 = Field(load=[0x24],
                min=None,
                max=None,
                size=8,
                help_str="Start character for the payload.",
                name='START_CHARACTER')
    f2 = Field(load=[0x56],
                min=None,
                max=None,
                size=8,
                help_str="CommandID.",
                name='COMMAND_ID')
    f3 = Field(load=None,
                   value=2,
                   min=None,
                   max=None,
                   size=8,
                   help_str="Payload size",
                   name='PAYLOAD_SIZE')
    f4 = Field(load=None,
                  min=None,
                  max=None,
                  size=8,
                  help_str="Header crc.",
                  name='HEADER_CRC')
    f5 = Field(load=None,
                  min=None,
                  max=None,
                  size=16,
                  help_str="Payload.",
                  name='PAYLOAD')
    f6 = Field(load=None,
                  min=None,
                  max=None,
                  size=16,
                  help_str="Start character for the payload.",
                  name='CRC')
    cmd.add_field(f1)
    cmd.add_field(f2)
    cmd.add_field(f3)
    cmd.add_field(f4)
    cmd.add_field(f5)
    cmd.add_field(f6)
    cmd.set_field('HEADER_CRC', 0x58)
    cmd.crc16_calculate(1,4,5)
    logger.info("Performing crc test: crc16_calculate:")
    logger.verbose(cmd.get_raw().hex().upper())

    from com.UARTCommunication import UARTCommunication
    com_if = UARTCommunication(port='COM12',baudrate=115200, timeout=1.0)
    com_if.open()
    com_if.write(cmd.get_raw())
    response = com_if.read(100)

    # Parsing the response according to CMD_BOARD_INFO structure
    board_ver = response[0]
    firmware_ver = struct.unpack('<H', response[1:3])[0]  # Little-endian unsigned short (2 bytes)
    state_flags = response[3]
    board_features = struct.unpack('<H', response[4:6])[0]  # Little-endian unsigned short (2 bytes)
    connection_flag = response[6]
    frw_extra_id = struct.unpack('<I', response[7:11])[0]  # Little-endian unsigned int (4 bytes)
    board_features_ext = struct.unpack('<H', response[11:13])[0]  # Little-endian unsigned short (2 bytes)
    reserved = response[13:16]
    base_frw_ver = struct.unpack('<H', response[16:18])[0]  # Little-endian unsigned short (2 bytes)

    # Printing the parsed values
    print(f"BOARD_VER: {board_ver/10}")

    print(f"FIRMWARE_VER: {firmware_ver}")
    print(f"STATE_FLAGS: {state_flags}")
    print(f"BOARD_FEATURES: {board_features}")
    print(f"CONNECTION_FLAG: {connection_flag}")
    print(f"FRW_EXTRA_ID: {frw_extra_id}")
    print(f"BOARD_FEATURES_EXT: {board_features_ext}")
    print(f"RESERVED: {reserved}")
    print(f"BASE_FRW_VER: {base_frw_ver}")
    com_if.close()

if __name__ == "__main__":
    main()
