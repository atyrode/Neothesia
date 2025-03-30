import os
import asyncio

import uvicorn
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from sysex import Keyboard

BLACK = "30"
RED = "31"
GREEN = "32"
YELLOW = "33"
BLUE = "34"
MAGENTA = "35"
CYAN = "36"
WHITE = "37"

term_width = os.get_terminal_size().columns
    
def cprint(message, color_code, prefix=None, top: bool = False, bottom: bool = False, sep: str = "=", end: str = "\n"):
    if top:
        print(f"{sep * term_width}")
    start_code = f"\033[{color_code}m"
    reset_code = "\033[0m"
    if prefix:
        print(f"[\033[35m{prefix}\033[0m] ", end="")
    print(f"{start_code}{message}{reset_code}", end=end)
    if bottom:
        print(f"{sep * term_width}")

def compute_note_color(note: int):
    color_list = ["red", "#red", "orange", "#orange", "yellow", "green", "#green", "cyan", "#cyan", "blue", "#blue", "purple",
                  "red2", "#red2", "orange2", "#orange2", "yellow2", "green2", "#green2", "cyan2", "#cyan2", "blue2", "#blue2", "purple2"]
    return color_list[note % len(color_list)]

def play(note: int):
    color = compute_note_color(note)
    cprint("PLAY:", GREEN, end="")
    cprint(f" {color}", WHITE)

def stop(note: int):
    color = compute_note_color(note)
    cprint("STOP:", RED, end="")
    cprint(f" {color}", WHITE)

def pressed(note: int):
    color = compute_note_color(note)
    cprint("PRESSED :", BLUE, end="")
    cprint(f" {color}", WHITE)
    controller["keyboard"].set_brightness(10)

def released(note: int):
    color = compute_note_color(note)
    cprint("RELEASED:", YELLOW, end="")
    cprint(f" {color}", WHITE)

def midi(payload: dict):

    source = payload["source"]

    if source == "system":
        if "device_name" in payload:
            pass
    else:
        active = payload["active"]
        key = int(payload["key"])
        
        controller[source][active](key)

controller = {
    "keyboard": None,
    "file": {
        True: play,
        False: stop,
    },
    "user": {
        True: pressed,
        False: released,
    },
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    controller["keyboard"] = Keyboard("LUMI Keys Block O8N0 Bluetooth")
    yield
    
app = FastAPI(lifespan=lifespan)

@app.post("/")
async def receive_message(request: Request):
    payload = await request.json()
    midi(payload)
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run("api:app", reload=True, host="0.0.0.0", port=8000, log_level="warning")