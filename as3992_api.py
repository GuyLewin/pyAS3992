import math
import glob
import struct
import serial

HEADER_LENGTH = 2
EPC_OFFSET_IN_COMMAND_RESULT = 8
NUMBER_OF_FREQ_BYTES = 3
TTY_USB_WILDCARD = "/dev/ttyUSB*"
UART_BAUD_RATE = 115200


def parse_rssi_i_q(rssi):
    rssi_i = (rssi & 0x0f) * 2
    rssi_q = (rssi >> 4) * 2
    return rssi_i, rssi_q, math.sqrt((rssi_i ** 2) + (rssi_q ** 2))


class AntennaDeviceCommunicator(object):
    def __init__(self):
        tty_over_usb_devices = glob.glob(TTY_USB_WILDCARD)
        assert len(tty_over_usb_devices) == 1, "Card not found or multiple cards connected"
        self._serial_conn = serial.Serial(tty_over_usb_devices[0], UART_BAUD_RATE)
   
    def send_command(self, command, data):
        command_header = struct.pack("BB", command, HEADER_LENGTH + len(data))
        command_buffer = command_header + data
        self._serial_conn.write(command_buffer)

    def receive_output(self):
        header = self._serial_conn.read(HEADER_LENGTH)
        command, length = struct.unpack("BB", header)
        output_buffer = self._serial_conn.read(length - HEADER_LENGTH)
        return command, length, output_buffer

    def send_and_receive_output(self, command, data):
        self.send_command(command, data)
        output_command, output_length, output_result = self.receive_output()
        assert command == output_command - 1, "Command result is for an unknown command: %d" % (output_command - 1,)
        return output_result


class AntennaDevice(object):
    def __init__(self):
        self._comm = AntennaDeviceCommunicator()
    
    def get_system_info(self):
        get_info_payload = lambda payload: self._comm.send_and_receive_output(0x10, payload)
        firmware_info = get_info_payload("\x00")
        hardware_info = get_info_payload("\x01")
        return firmware_info, hardware_info

    def _change_freq(self, is_hopping, freq_khz, rssi_threshold=-40):
        if is_hopping:
            # Add frequency to list of hopping frequencies
            mask = 0x40
        else:
            # Clear the list and add only this frequency (not hopping)
            mask = 0x80
        payload = struct.pack("B", mask)
        # Only 3 bytes of frequency
        payload += struct.pack("<I", freq_khz)[:NUMBER_OF_FREQ_BYTES]
        payload += struct.pack("b", rssi_threshold)
        self._comm.send_and_receive_output(0x41, payload)

    def set_profile(self, start_freq_khz, end_freq_khz, freq_increment_khz, rssi_threshold):
        is_hopping = False
        for freq in xrange(start_freq_khz, end_freq_khz, freq_increment_khz):
            print "Adding %d to frequency list" % (freq,)
            self._change_freq(is_hopping, freq, rssi_threshold=rssi_threshold)
            is_hopping = True

    def set_antenna_state(self, is_on):
        if is_on:
            payload = "\xff"
        else:
            payload = "\x00"
        self._comm.send_and_receive_output(0x18, payload)

    def iter_epc_rssi(self):
        self._comm.send_command(0x43, "\x01")
        remaining_tags = 1
        while remaining_tags > 0:
            _, _, command_result = self._comm.receive_output()
            if len(command_result.strip("\x00")) == 0:
                # Sometimes the answer is just empty
                raise StopIteration
            found_tags, rssi, _, _, _, epc_length, _ = struct.unpack(">BBBBBBH", command_result[:EPC_OFFSET_IN_COMMAND_RESULT])
            if found_tags > 0:
                epc = command_result[EPC_OFFSET_IN_COMMAND_RESULT:EPC_OFFSET_IN_COMMAND_RESULT + epc_length]
                yield epc, parse_rssi_i_q(rssi)
            remaining_tags = found_tags - 1

