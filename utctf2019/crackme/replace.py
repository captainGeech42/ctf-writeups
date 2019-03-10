#!/usr/bin/env python

with open("crackme", "rb") as f:
    original = f.read()

with open("stuff_func.bin", "rb") as f:
    newfunc = f.read()

offset = 0xaf0
padding = b"\x90"*80

new = original[:offset] + newfunc + padding + original[offset+len(newfunc)+len(padding):]

with open("crackme.newfunc", "wb") as f:
    f.write(new)
