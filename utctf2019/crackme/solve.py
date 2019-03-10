#!/usr/bin/env python3

with open("test.bin", "rb") as f:
    flag = f.read()

# undo stuff func
asdf = ""
for x in range(len(flag)):
    asdf += chr(flag[x] ^ (x + 51))

# undo the 0x27 xor
before_27 = ""
for t in asdf:
    before_27 += chr(ord(t) ^ 0x27)

print(repr(before_27))
