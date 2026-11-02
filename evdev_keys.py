"""
evdev_keys – keyboard reader for TCA8418 (CardputerZero) and USB Pico (PT35).
Auto-detects keyboard device and selects the appropriate keymap.
"""
import os
import threading
import time

import evdev

# --- Keymaps ---------------------------------------------------------------
_KEYMAP_TCA8418 = {
    103: 'KEY_UP_PIN',
    108: 'KEY_DOWN_PIN',
    105: 'KEY_LEFT_PIN',
    106: 'KEY_RIGHT_PIN',
    33:  'KEY_UP_PIN',
    44:  'KEY_LEFT_PIN',
    45:  'KEY_DOWN_PIN',
    46:  'KEY_RIGHT_PIN',
    28:  'KEY_PRESS_PIN',
    1:   'KEY3_PIN',
    57:  'KEY1_PIN',
    14:  'KEY2_PIN',
    15:  'KEY3_PIN',
}
_KEYMAP_USB = {
    103: 'KEY_UP_PIN',
    108: 'KEY_DOWN_PIN',
    105: 'KEY_LEFT_PIN',
    106: 'KEY_RIGHT_PIN',
    28:  'KEY_PRESS_PIN',
    99:  'KEY1_PIN',
    119: 'KEY2_PIN',
    14:  'KEY3_PIN',
}

# --- Device detection ------------------------------------------------------
def _device_name(path):
    """Resolve human-readable device name for an event node."""
    try:
        base = os.path.basename(os.path.realpath(path))
        with open(f'/sys/class/input/{base}/device/name') as f:
            return f.read().lower()
    except Exception:
        return ''

def _find_keyboard_device():
    env = os.environ.get('RJ_KEYBOARD_DEVICE', '')
    if env:
        name = _device_name(env)
        if 'pico' in name or 'usb-' in env:
            return env, _KEYMAP_USB
        return env, _KEYMAP_TCA8418
    for i in range(8):
        path = f'/dev/input/event{i}'
        name = _device_name(path)
        if 'tca8418' in name:
            return path, _KEYMAP_TCA8418
        if 'pico' in name:
            return path, _KEYMAP_USB
    return '/dev/input/event3', _KEYMAP_TCA8418

EVDEV_DEVICE, _KEYMAP = _find_keyboard_device()

_REVERSE_MAP = {}
for _code, _name in _KEYMAP.items():
    _REVERSE_MAP.setdefault(_name, []).append(_code)

# --- State ----------------------------------------------------------------
_key_state = {}
_lock = threading.Lock()
_device = None
_thread = None
_PAUSE_FLAG = "/dev/shm/rj_evdev_pause"

# --- Reader ---------------------------------------------------------------
def _reader_loop():
    global _device
    while True:
        try:
            if os.path.exists(_PAUSE_FLAG):
                if _device:
                    try:
                        _device.close()
                    except Exception:
                        pass
                    _device = None
                time.sleep(0.2)
                continue
            if _device is None:
                _device = evdev.InputDevice(EVDEV_DEVICE)
            for event in _device.read_loop():
                if os.path.exists(_PAUSE_FLAG):
                    try:
                        _device.close()
                    except Exception:
                        pass
                    _device = None
                    break
                if event.type != evdev.ecodes.EV_KEY:
                    continue
                with _lock:
                    _key_state[event.code] = event.value > 0
        except Exception:
            _device = None
            time.sleep(0.5)

def start():
    global _thread
    if _thread is not None:
        return
    _thread = threading.Thread(target=_reader_loop, daemon=True)
    _thread.start()

# --- Public API -----------------------------------------------------------
def is_pressed(button_name):
    codes = _REVERSE_MAP.get(button_name, [])
    with _lock:
        return any(_key_state.get(c, False) for c in codes)

def is_key_pressed(evdev_code):
    with _lock:
        return _key_state.get(evdev_code, False)

def any_pressed():
    with _lock:
        return any(_key_state.values())

def get_pressed_button():
    with _lock:
        for code, pressed in _key_state.items():
            if pressed and code in _KEYMAP:
                return _KEYMAP[code]
    return None

def pause():
    try:
        with open(_PAUSE_FLAG, "w"):
            pass
    except Exception:
        pass
    time.sleep(0.3)

def resume():
    try:
        os.unlink(_PAUSE_FLAG)
    except OSError:
        pass

if not os.path.exists(_PAUSE_FLAG):
    start()