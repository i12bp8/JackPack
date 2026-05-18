"""Headless keyboard compatibility shim for JackPack."""


def is_pressed(button_name: str) -> bool:
    return False


def is_key_pressed(code: int) -> bool:
    return False


def get_pressed_button():
    return None
