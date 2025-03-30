import asyncio
import time
from dataclasses import dataclass, field

import mido

# Sysex LUMI commands look like:
# F0 <manufacturer> 77 <device-id> <command> <checksum> F7

START = [0xf0]
ROLI = [0x00, 0x21, 0x10]
UNKNOWN = [0x77]
LUMI = [0x00]
END = [0xf7]

MIDI_DEVICE_NAME = "LUMI Keys Block 1B15 Bluetooth"

@dataclass
class SysEx:
    manufacturer: list[int]
    unknown: list[int]
    device_id: list[int]

    @staticmethod
    def checksum(values):
        sum_value = len(values)
        for value in values:
            sum_value = (sum_value * 3 + value) & 0xff
        return [sum_value & 0x7f]
    
    def compute(self, command):

        data = self.manufacturer.copy()
        data += self.unknown.copy()
        data += self.device_id.copy()
        data += command.copy()
        data += self.checksum(command).copy()

        hex_values = ' '.join([f'{value:02X}' for value in data])
        print(f"[  Sent  ]: '{hex_values}'")
        return data
    
    def parse(self, message: mido.Message):
        data = list(message.data)
        if data == [0, 33, 16, 119, 102, 0, 0, 0, 0, 32, 0, 0, 109]:
            return
        hex_values = ' '.join([f'{value:02X}' for value in data])
        print(f"[Received]: '{hex_values}'")
        print(f"===============================================================")
    
    def send(self, output_port, command, raw=False):
        if type(command) == str:
            command = self.str_to_int(command)
        data = command
        if not raw:
            data = self.compute(command)
        message = mido.Message("sysex", data=data)
        output_port.send(message)
        output_port.close()

    @staticmethod
    def str_to_int(string) -> list[int]:
        """Translates something like:
        00 21 10 77 66 00 00 00 00 10 10 20 00 00 66 25 61 18 6A 1C 68 29 58 61 1A 6A 18 61 58 1A 13 42 41 49 21 4C 6B 4C 2B 0E 60 41 29 00 00 1D
        into a list of integers.
        """
        return [int(value, 16) for value in string.split()]
    
@dataclass
class KeyboardEvent:
    active: bool
    key: int
    velocity: int
    time: int

class Keyboard:
    def __init__(self, name: str):
        self.midi_device_name = name
        self.output = mido.open_output(self.midi_device_name)
        self.sysex = SysEx(ROLI, UNKNOWN, LUMI)
        self.history: list[KeyboardEvent] = []
        asyncio.create_task(self.listen_to_midi())
    
    async def listen_to_midi(self):
        input_port = mido.open_input()
        print("Listening for MIDI input...")

        while True:
            for message in input_port.iter_pending():
                
                if message.type == 'sysex':
                    continue
                    self.sysex.parse(message)

                # self.history.append(KeyboardEvent(active=message.type == 'note_on', key=message.note, velocity=message.velocity, time=time.time()))
                
                if message.type in ['note_on', 'note_off']:

                    if message.type == 'note_on':
                        ripple_effect_task = asyncio.create_task(self.ripple_effect(message.note))
                        print(f"Received {message.type} message: Note {message.note}, Velocity {message.velocity}")
            
            await asyncio.sleep(0.01)
    
    async def dim_note(self, note: int):
        """Gradually reduce the velocity of a note and then send a note_off message."""
        await asyncio.sleep(0.1)
        self.output.send(mido.Message('note_off', note=note, velocity=0))

    async def ripple_effect(self, note: int):
        """Receive a note and send message to note_on the notes around it, then dim them."""
        ripple_strength = 10
        for shift in range(1, ripple_strength):
            forward = min(127, max(0, note + shift))
            backward = min(127, max(0, note - shift))
            
            # Send note_on for forward and backward notes
            self.output.send(mido.Message('note_on', note=forward, velocity=20))
            self.output.send(mido.Message('note_on', note=backward, velocity=20))
            
            # Create a subtask for dimming each note
            asyncio.create_task(self.dim_note(forward))
            asyncio.create_task(self.dim_note(backward))
            await asyncio.sleep(0.05)

    def send(self, command):
        if self.midi_device_name in mido.get_output_names():
            self.sysex.send(command)
        else:
            raise ValueError(f"Device not found.")
        
class BitArray:
    def __init__(self):
        self.values = []
        self.num_bits = 0

    def append(self, value, size=7):
        current = self.num_bits // 7
        used_bits = self.num_bits % 7
        packed = 0

        if used_bits > 0:
            packed = self.values.pop()

        self.num_bits += size

        while size > 0:
            packed |= (value << used_bits) & 127
            size -= (7 - used_bits)
            value >>= (7 - used_bits)
            self.values.append(packed)
            packed = 0
            used_bits = 0

    def get(self, size=32):
        while len(self.values) < 8:
            self.values.append(0)
        return self.values