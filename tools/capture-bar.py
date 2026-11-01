#!/usr/bin/env python3
"""Read only the top 32 pixels of an X11 screen into PPM on stdout."""
import ctypes as C
import sys
x=C.CDLL("libX11.so.6")
x.XOpenDisplay.argtypes=[C.c_char_p]; x.XOpenDisplay.restype=C.c_void_p
x.XDefaultRootWindow.argtypes=[C.c_void_p]; x.XDefaultRootWindow.restype=C.c_ulong
x.XDisplayWidth.argtypes=[C.c_void_p,C.c_int]; x.XDisplayWidth.restype=C.c_int
x.XGetImage.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_ulong,C.c_int]; x.XGetImage.restype=C.c_void_p
x.XGetPixel.argtypes=[C.c_void_p,C.c_int,C.c_int]; x.XGetPixel.restype=C.c_ulong
x.XDestroyImage.argtypes=[C.c_void_p]; x.XCloseDisplay.argtypes=[C.c_void_p]
d=x.XOpenDisplay(b":0")
if not d: raise SystemExit("Cannot open X display")
w=x.XDisplayWidth(d,0); h=32
img=x.XGetImage(d,x.XDefaultRootWindow(d),0,0,w,h,C.c_ulong(-1).value,2)
if not img: raise SystemExit("Cannot read bar")
try:
    pixels=bytearray()
    for row in range(h):
        for col in range(w):
            p=x.XGetPixel(img,col,row)
            pixels.extend(((p>>16)&255,(p>>8)&255,p&255))
    sys.stdout.buffer.write(f"P6\n{w} {h}\n255\n".encode()+pixels)
finally:
    x.XDestroyImage(img); x.XCloseDisplay(d)
