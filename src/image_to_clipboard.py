#!/usr/bin/python3

# Image to clipboard, only works on windows

import sys
from PIL import Image
from io import BytesIO

try:
    import win32clipboard
except ImportError:
    pass

def image_to_clipboard(image: Image):
    if sys.platform != 'win32':
        print('Copying to clipboard is currently only available for Windows.')
        return

    def send_to_clipboard(clip_type, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()
    
    output = BytesIO()
    image.save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    send_to_clipboard(win32clipboard.CF_DIB, data)
    return