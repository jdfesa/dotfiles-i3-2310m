#!/usr/bin/python3
"""Keep audio positioning data in X memory; measure Pango only on demand."""
import ctypes as C
import json
import math
import re

PROPERTY = b"_BGH_AUDIO_BAR_SUFFIX"
FIELDS = ("full_text", "markup", "min_width", "separator_block_width")


def suffix(blocks):
    index = next((i for i, block in enumerate(blocks)
                  if (block.get("name"), block.get("instance")) == ("volume", "usb-output")), None)
    return [{key: block[key] for key in FIELDS if key in block} for block in blocks[index:]] if index is not None else []


class PositionMemory:
    def __init__(self):
        self.x = C.CDLL("libX11.so.6")
        ptr, ulong, integer = C.c_void_p, C.c_ulong, C.c_int
        up, ip = C.POINTER(ulong), C.POINTER(integer)
        signatures = {
            "XOpenDisplay": (ptr, [C.c_char_p]), "XCloseDisplay": (integer, [ptr]),
            "XDefaultRootWindow": (ulong, [ptr]),
            "XInternAtom": (ulong, [ptr, C.c_char_p, integer]),
            "XChangeProperty": (integer, [ptr, ulong, ulong, ulong, integer, integer, ptr, integer]),
            "XGetWindowProperty": (integer, [ptr, ulong, ulong, C.c_long, C.c_long, integer, ulong,
                                             up, ip, up, up, C.POINTER(ptr)]),
            "XFree": (integer, [ptr]), "XFlush": (integer, [ptr]),
            "XResourceManagerString": (C.c_char_p, [ptr]),
            "XDefaultScreen": (integer, [ptr]),
            "XDisplayHeight": (integer, [ptr, integer]),
            "XDisplayHeightMM": (integer, [ptr, integer]),
        }
        for name, (result, args) in signatures.items():
            function = getattr(self.x, name)
            function.restype, function.argtypes = result, args
        self.display = self.x.XOpenDisplay(None)
        self.previous = None
        if not self.display:
            raise OSError("An X11 display is required for audio panel positioning.")
        self.root = self.x.XDefaultRootWindow(self.display)
        self.atom = self.x.XInternAtom(self.display, PROPERTY, False)
        self.utf8 = self.x.XInternAtom(self.display, b"UTF8_STRING", False)

    def publish(self, blocks):
        data = json.dumps(suffix(blocks), ensure_ascii=False, separators=(",", ":")).encode()
        if data == self.previous or len(data) > 65536:
            return
        self.x.XChangeProperty(self.display, self.root, self.atom, self.utf8, 8, 0,
                               C.cast(C.c_char_p(data), C.c_void_p), len(data))
        self.x.XFlush(self.display)
        self.previous = data

    def read(self):
        kind, fmt, count, after, data = C.c_ulong(), C.c_int(), C.c_ulong(), C.c_ulong(), C.c_void_p()
        try:
            result = self.x.XGetWindowProperty(self.display, self.root, self.atom, 0, 16384, False,
                                              self.utf8, C.byref(kind), C.byref(fmt), C.byref(count),
                                              C.byref(after), C.byref(data))
            if result or kind.value != self.utf8 or fmt.value != 8 or after.value or not data:
                raise RuntimeError("Audio bar position is not available yet.")
            blocks = json.loads(C.string_at(data, count.value))
            if (not isinstance(blocks, list) or not 1 <= len(blocks) <= 64 or
                    not all(isinstance(block, dict) for block in blocks)):
                raise ValueError("Invalid audio positioning data.")
            return blocks
        finally:
            if data:
                self.x.XFree(data)

    def dpi(self):
        resources = self.x.XResourceManagerString(self.display) or b""
        match = re.search(rb"(?m)^Xft\.dpi\s*:\s*([0-9.]+)\s*$", resources)
        if match:
            value = float(match[1])
            if math.isfinite(value) and 40 <= value <= 600:
                return math.floor(value + 0.5)
        screen = self.x.XDefaultScreen(self.display)
        mm = self.x.XDisplayHeightMM(self.display, screen)
        return int(self.x.XDisplayHeight(self.display, screen) * 25.4 / mm) if mm > 0 else 96

    def close(self):
        if self.display:
            self.x.XCloseDisplay(self.display)
            self.display = None


def find_bar(node, output):
    if node.get("type") == "output":
        if node.get("name") != output:
            return None
        output = None
    props = node.get("window_properties", {})
    if output is None and props.get("class") == "i3bar":
        return node
    for child in node.get("nodes", []) + node.get("floating_nodes", []):
        found = find_bar(child, output)
        if found:
            return found
    return None


def measure_blocks(blocks, font, dpi):
    import gi
    gi.require_version("Pango", "1.0")
    gi.require_version("PangoCairo", "1.0")
    from gi.repository import Pango, PangoCairo
    context = PangoCairo.FontMap.get_default().create_context()
    PangoCairo.context_set_resolution(context, dpi)
    layout = Pango.Layout.new(context)
    layout.set_font_description(Pango.FontDescription.from_string(font))
    widths = []
    for block in blocks:
        text = block.get("full_text")
        minimum, separator = block.get("min_width", 0), block.get("separator_block_width", 9)
        if (not isinstance(text, str) or len(text) > 4096 or
                type(minimum) is not int or not 0 <= minimum <= 4096 or
                type(separator) is not int or not 0 <= separator <= 256):
            raise ValueError("Invalid audio positioning block.")
        if block.get("markup") == "pango":
            layout.set_markup(text, -1)
        else:
            layout.set_text(text, -1)
        width = max(minimum, layout.get_pixel_size()[0]) if text else 0
        widths.append((width, separator))
    return widths


def anchor_from_widths(rect, widths, padding=0):
    if (not widths or widths[0][0] <= 0 or type(padding) is not int or
            not 0 <= padding <= 4096):
        raise ValueError("Audio block is unavailable.")
    total = sum(width + (separator if i < len(widths) - 1 else 0)
                for i, (width, separator) in enumerate(widths) if width)
    center = rect["x"] + rect["width"] - padding - total + widths[0][0] // 2
    if not rect["x"] <= center < rect["x"] + rect["width"]:
        raise ValueError("Audio block is outside the bar.")
    return center, rect["y"] + rect["height"]


def keyboard_anchor(ipc, tree):
    focused = next((w for w in ipc.request(1) if w.get("focused")), None)
    bar = find_bar(tree, focused["output"]) if focused else None
    if bar is None:
        raise RuntimeError("The focused output has no audio bar.")
    settings = ipc.request(6, bar["window_properties"]["instance"])
    font = settings.get("font", "")
    if settings.get("position") != "top" or not font.startswith("pango:"):
        raise RuntimeError("Audio positioning requires the configured top Pango bar.")
    memory = PositionMemory()
    try:
        dpi = memory.dpi()
        widths = measure_blocks(memory.read(), font[6:], dpi)
        padding = settings.get("padding", {}).get("width", 0)
        return anchor_from_widths(bar["rect"], widths, padding)
    finally:
        memory.close()
