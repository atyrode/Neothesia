import asyncio
import mido
from sysex import Keyboard

async def main():
    # Initialize the keyboard
    keyboard = Keyboard("LUMI Keys Block O8N0 Bluetooth")
    
    # Notes to light up (71, 69, 67, 65)
    notes = [71, 69, 67, 65]
    
    # Light up each note
    for note in notes:
        # Send note_on with maximum velocity (127) for white color
        keyboard.output.send(mido.Message('note_on', note=note, velocity=127))
        print(f"Lit up note {note}")
    
    # Keep the program running to maintain the lights
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Turn off all notes when the program is interrupted
        for note in notes:
            keyboard.output.send(mido.Message('note_off', note=note, velocity=0))
        print("\nTurned off all notes")
        keyboard.output.close()

if __name__ == "__main__":
    asyncio.run(main()) 