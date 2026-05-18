"""Headless LCD compatibility layer for JackPack.

Legacy RaspyJack payloads render to a small Waveshare LCD. JackPack has no
physical display, so ``LCD_ShowImage`` optionally mirrors the latest frame to
``/dev/shm`` for diagnostics while all hardware calls stay no-ops.
"""

from __future__ import annotations

import os
import time
from pathlib import Path


LCD_WIDTH = 128
LCD_HEIGHT = 128
LCD_X = 0
LCD_Y = 0
LCD_X_MAXPIXEL = 128
LCD_Y_MAXPIXEL = 128
LCD_SCALE = 1.0

U2D_R2L = 6
D2U_L2R = 7
D2U_R2L = 8
SCAN_DIR_DFT = U2D_R2L

_FRAME_MIRROR_PATH = Path(os.environ.get("RJ_FRAME_PATH", "/dev/shm/raspyjack_last.jpg"))
_RAW_FRAME_PATH = Path(os.environ.get("RJ_RAW_FRAME_PATH", "/dev/shm/raspyjack_raw.rgb"))
_FRAME_MIRROR_ENABLED = os.environ.get("RJ_FRAME_MIRROR", "1") != "0"
_FRAME_INTERVAL = 1.0 / max(1.0, float(os.environ.get("RJ_FRAME_FPS", "5")))
_last_frame_save = 0.0


def S(value):
    return int(value)


class LCD:
    width = LCD_WIDTH
    height = LCD_HEIGHT
    display_type = "HEADLESS_128"

    def __init__(self):
        self.width = LCD_WIDTH
        self.height = LCD_HEIGHT
        self.LCD_Scan_Dir = SCAN_DIR_DFT
        self.LCD_X_Adjust = LCD_X
        self.LCD_Y_Adjust = LCD_Y
        self.display_type = "HEADLESS_128"

    def LCD_Init(self, Lcd_ScanDir=None):
        self.LCD_Scan_Dir = Lcd_ScanDir or SCAN_DIR_DFT
        return 0

    def LCD_Clear(self):
        return None

    def LCD_Reset(self):
        return None

    def LCD_WriteReg(self, Reg):
        return None

    def LCD_WriteData_8bit(self, Data):
        return None

    def LCD_WriteData_NLen16Bit(self, Data, DataLen):
        return None

    def LCD_SetGramScanWay(self, scan_dir):
        self.LCD_Scan_Dir = scan_dir
        return None

    def LCD_SetWindows(self, Xstart, Ystart, Xend, Yend):
        return None

    def LCD_ShowImage(self, Image, Xstart=0, Ystart=0):
        if Image is None or not _FRAME_MIRROR_ENABLED:
            return None

        global _last_frame_save
        now = time.monotonic()
        if now - _last_frame_save < _FRAME_INTERVAL:
            return None

        _last_frame_save = now
        try:
            frame = Image.convert("RGB").resize((self.width, self.height))
            _FRAME_MIRROR_PATH.parent.mkdir(parents=True, exist_ok=True)
            frame.save(_FRAME_MIRROR_PATH, "JPEG", quality=76)
            try:
                _RAW_FRAME_PATH.write_bytes(frame.tobytes())
            except Exception:
                pass
        except Exception:
            pass
        return None
