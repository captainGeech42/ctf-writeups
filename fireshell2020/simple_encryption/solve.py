#!/usr/bin/env python3

import string
import subprocess

alphabet = string.printable

with open("alpha.in", "w") as f:
    f.write(alphabet)

subprocess.run(["./chall", "alpha.in", "alpha.out"])

key = {}

with open("alpha.out", "rb") as f:
    for i in range(len(alphabet)):
        key[alphabet[i]] = f.read(1)

in_list = list(key.values())
out_list = list(key.keys())
flag = ""

with open("flag.enc", "rb") as f:
    data = f.read()

for d in data:
    b = bytes([d])
    assert(b in in_list)

    flag += out_list[in_list.index(b)]

print(flag)
