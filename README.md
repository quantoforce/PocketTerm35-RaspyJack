# PocketTerm35-RaspyJack

Fork of [RaspyJack](https://github.com/7h30th3r0n3/Raspyjack) with **native support for PocketTerm35**.

The original project is a portable Raspberry Pi offensive toolkit with an LCD-driven interface, WebUI, and Payload IDE. For the full feature list, payloads, and general documentation, please refer to the original repository: https://github.com/7h30th3r0n3/Raspyjack

## What's new in this fork?

- **PocketTerm35 Display (640×480):** Native Linux framebuffer support (`/dev/fb0`), bypassing SPI/GPIO entirely.
- **USB Pico Keyboard Input:** Handled via evdev (`evdev_keys.py`).
- **Unified `gpio_shim`:** Allows existing payloads to work without modification by translating `RPi.GPIO.input()` calls into evdev key states.
- **`POCKETTERM_640` Profile:** Added to the installer and `gui_conf.json`.

## Install

```bash
sudo apt update && sudo apt install -y git
sudo -i
git clone https://github.com/quantoforce/PocketTerm35-RaspyJack.git Raspyjack
cd Raspyjack
chmod +x install_raspyjack.sh
./install_raspyjack.sh
reboot
```

> **Important:** When prompted for the display, choose **4) POCKETTERM_640**.

## Input Mapping

| Control | Action |
|---|---|
| UP / DOWN / LEFT / RIGHT | Navigate |
| Enter | OK |
| Select | KEY1 |
| Start | KEY2 |
| Del | KEY3 |

On PocketTerm35, input is read from the USB Pico keyboard. The button mapping remains the same as on the original hardware.

## Documentation

For payload creation, WebUI usage, attack flows, and everything else, see the original project:
https://github.com/7h30th3r0n3/Raspyjack

## License & Safety

Licensed under MIT. For **authorized security testing, research, and education only**.
