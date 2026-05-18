"""Headless LCD hardware compatibility shim for JackPack."""

LCD_RST_PIN = -1
LCD_DC_PIN = -1
LCD_CS_PIN = -1
LCD_BL_PIN = -1
FB_SIZE = 128 * 128 * 2


class _SpiStub:
    max_speed_hz = 0
    mode = 0

    def writebytes(self, data):
        return None


SPI = _SpiStub()


def epd_digital_write(pin, value):
    return None


def Driver_Delay_ms(xms):
    return None


def SPI_Write_Byte(data):
    return None


def GPIO_Init():
    return 0


def fb_write(data: bytes):
    return None
