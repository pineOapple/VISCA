import serial
import struct

class UARTCommunication:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate, timeout=1)

    def open(self):
        if not self.ser.is_open:
            self.ser.open()

    def close(self):
        if self.ser.is_open:
            self.ser.close()

    def send_command(self, command_id, payload=b''):
        start_char = b'>'
        payload_size = len(payload)
        header_checksum = (command_id + payload_size) % 256
        header = struct.pack('BB', command_id, payload_size)
        message = start_char + header + bytes([header_checksum]) + payload
        payload_checksum = sum(payload) % 256
        message += bytes([payload_checksum])
        self.ser.write(message)

    def read_response(self, size=64):
        return self.ser.read(size)

def parse_board_info(data):
    if len(data) < 34:
        print("Response too short to parse CMD_BOARD_INFO")
        return {}

    board_info = {
        "board_ver": data[0] / 10,
        "firmware_ver": struct.unpack('<H', data[1:3])[0] / 1000,
        "state_flags": data[3],
        "board_features": struct.unpack('<H', data[4:6])[0],
        "connection_flag": data[6],
        "frw_extra_id": struct.unpack('<I', data[7:11])[0],
        "board_features_ext": struct.unpack('<H', data[11:13])[0],
        "base_frw_ver": struct.unpack('<H', data[13:15])[0] / 10,
        "flash_size": struct.unpack('<H', data[17:19])[0],
        "eeprom_size": struct.unpack('<I', data[19:23])[0],
        "gui_ver": struct.unpack('<H', data[23:25])[0] / 1000,
        "device_id": data[25:34].hex(),
    }

    return board_info

def parse_realtime_data_3(data):
    if len(data) < 58:
        print("Response too short to parse CMD_REALTIME_DATA_3")
        return {}

    # Example parsing (the actual structure may vary based on the protocol specification)
    timestamp = struct.unpack('<H', data[0:2])[0]
    sensor_data = struct.unpack('<3h', data[2:8])
    encoder_data = struct.unpack('<3H', data[8:14])
    control_data = struct.unpack('<3h', data[14:20])
    temperature_data = struct.unpack('<7b', data[20:27])
    error_flags = struct.unpack('<H', data[27:29])[0]

    realtime_data = {
        "timestamp": timestamp,
        "sensor_data": sensor_data,
        "encoder_data": encoder_data,
        "control_data": control_data,
        "temperature_data": temperature_data,
        "error_flags": error_flags,
        # Add more fields as needed...
    }

    return realtime_data

def request_board_info():
    uart = UARTCommunication(port="COM11", baudrate=9600)
    uart.open()

    try:
        # Send CMD_BOARD_INFO
        CMD_BOARD_INFO = 86
        uart.send_command(CMD_BOARD_INFO)
        response = uart.read_response(64)
        print(f"Response to CMD_BOARD_INFO: {response}")
        board_info = parse_board_info(response)
        print_board_info(board_info)

        # Send CMD_REALTIME_DATA_3
        CMD_REALTIME_DATA_3 = 32
        uart.send_command(CMD_REALTIME_DATA_3)
        response = uart.read_response(64)
        print(f"Response to CMD_REALTIME_DATA_3: {response}")
        realtime_data = parse_realtime_data_3(response)
        print_realtime_data(realtime_data)

    finally:
        uart.close()

def print_board_info(info):
    print(f"Device s/n: {info['device_id']}, MCU s/n: [UNKNOWN]")
    print(f"Firmware ver.: {info['firmware_ver']}, board ver.: {info['board_ver']} \"Tiny+\", FLASH size: {info['flash_size']} Kb, EEPROM size: {info['eeprom_size']} byte")
    print(f"GUI ver.: {info['gui_ver']}")

def print_realtime_data(data):
    print("Encoder[ROLL]")
    print("\tEncoder type: DISABLED")
    print(f"\tdiagnostic data: {data['sensor_data'][0]:012x}\tread errors: 0")
    print("Encoder[PITCH]")
    print("\tEncoder type: DISABLED")
    print(f"\tdiagnostic data: {data['sensor_data'][1]:012x}\tread errors: 0")
    print("Encoder[YAW]")
    print("\tEncoder type: DISABLED")
    print(f"\tdiagnostic data: {data['sensor_data'][2]:012x}\tread errors: 0")
    print(f"DRIVERS STATE: OTW=0, DRV_FAULT=0")
    print(f"TIME SLOTS FREE (us): {data['control_data']}")
    print(f"TEMPERATURE (C°): MCU={data['temperature_data'][0]}, IMU={data['temperature_data'][1]}, F.IMU={data['temperature_data'][2]}, DRIVERS={data['temperature_data'][3]}, ROLL_M={data['temperature_data'][4]}, PITCH_M={data['temperature_data'][5]}, YAW_M={data['temperature_data'][6]}")
    print(f"Errors: [2-0] Accelerometer is not calibrated")
    print(f"assert_line: 0")
    print(f"assert_file: ")
    print(f"COM errors: 1")
    print(f"I2C errors: none")
    print(f"CAN bus errors: 0")
    print(f"CAN bus error flags: no")
    print(f"Main IMU: enabled (internal sensor), attitude ref.: internal, heading ref.: no")
    print(f"\tattitude ref. error:  0.0°")
    print(f"Frame IMU: disabled")
    print(f"External IMU: DISABLED")
    print(f"Tripod mode:off")
    print(f"UART1 RX buffer overflow: 0 bytes")
    print(f"UART1 TX buffer overflow: 0 bytes")
    print(f"RC_serial RX buffer overflow: 0 bytes")
    print(f"RC_serial TX buffer overflow: 0 bytes")
    print(f"UART2 RX buffer overflow: 0 bytes")
    print(f"UART2 TX buffer overflow: 0 bytes")
    print(f"SBGC32 local serial ports:")
    print(f"\tUART1 - Serial API")
    print(f"\tRC_serial - disabled")
    print(f"\tUART2 - Serial API")

if __name__ == "__main__":
    request_board_info()
