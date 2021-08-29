"""
0000038e  70c708   rd r6, r7, r8
00000391  61260c   shl r9, r6, r12
00000394  69460b   shr r10, r6, r11
00000397  30c90a   or r6, r9, r10
0000039a  00c601   add r6, r6, r1
0000039d  40c600   xor r6, r6, r0
000003a0  10c602   sub r6, r6, r2
000003a3  a837     io r6, 0x7
000003a5  090801   addi r8, r8, 0x1
000003a8  090800   addi r8, r8, 0x0
000003ab  088401   addi r4, r4, 0x1
000003ae  28201f   cmpi r4, 0x1f
000003b1  90038e   jne 0x38e

000003b4  b89131   halt
"""

import sys

from fixedint import UInt8 # pip install fixedint

data = b"\x911\x01\r1\xcb\x85\xbf\xa8\xd7\x08\xe4\xe4\xf79=\xec\xf7\xe09\xf3\x10\xff\x109\xe8\xf3EE\xf7\xa0"

def rd(a2, a3):
    offset = a2 << 8 | a3
    offset -= 0x3b5

    return data[offset]

# 3 bytes of input
# byte 0 -> r1
# byte 1 -> r0
# byte 2 -> r2

# zero'd regs: r5, r11, r12, r7, r8

def test_sol(b0, b1, b2):
    # initial reg values
    r5 = UInt8(0xb)
    r11 = UInt8(0x2)
    r12 = UInt8(0x6)
    r7 = UInt8(0x3)
    r8 = UInt8(0xb5)

    # input bytes
    r0 = UInt8(b1)
    r1 = UInt8(b0)
    r2 = UInt8(b2)

    # counter
    r4 = UInt8(0)
    out_str = b""
    while r4 != 0x1f:
        r6 = rd(r7, r8)
        r9 = r6 << r12
        r10 = r6 >> r11
        r6 = r9 | r10
        r6 += r1
        r6 ^= r0
        r6 -= r2
        out_str += bytes([r6])

        r8 += 1
        r4 += 1
    
    return out_str

for a in range(20, 128):
    for b in range(20, 128):
        for c in range(20, 128):
            x = test_sol(a, b, c)
            if b"YauzaCTF{" in x:
                print(x)
                sys.exit(0)
