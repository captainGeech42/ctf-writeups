#!/usr/bin/env python3

import json
from pprint import pprint

def is_printable(char):
    return char >= 0x21 and char <= 0x7e

def append(s, c): 
    c = int(c, 16)
    if is_printable(c):
        s += chr(c)
    return s

# read in json data
with open("ev3_dest_data.json", "r") as f:
    data = json.load(f)

# [ 0 - 6 ] don't care
# [ 7 - 8 ] write text cmd
# [ 9 - d ] color, position
# [ e - (n-3) ] data, \0 term

chars = []

for packet in data:
    layers = packet["_source"]["layers"]

    if "data" in layers:
        data = layers["data"]
        length = int(data["data.len"])
        raw_hex = data["data.data"].split(":")

        if length == 19:
            x = int(raw_hex[10], 16)
            y = int(raw_hex[12], 16)
            char = chr(int(raw_hex[14], 16))
        elif length == 20:
            for i in range(10, 13):
                if int(raw_hex[i], 16) < 0x80:
                    x = int(raw_hex[i], 16)
                    break
            y = int(raw_hex[13], 16)
            char = chr(int(raw_hex[15], 16))
        elif length == 21:
            for i in range(10, 14):
                if int(raw_hex[i], 16) < 0x80:
                    x = int(raw_hex[i], 16)
                    break
            x = int(raw_hex[11], 16)
            for i in range(14, 18):
                if int(raw_hex[i], 16) < 0x80:
                    y = int(raw_hex[i], 16)
                    break
            char = chr(int(raw_hex[16], 16))
        else:
            continue
            
        chars.append({"length": length, "x": x, "y": y, "char": char})

# i got this function off stack overflow, don't have the link
def sortkeypicker(keynames):
    negate = set()
    for i, k in enumerate(keynames):
        if k[:1] == '-':
            keynames[i] = k[1:]
            negate.add(k[1:])
    def getit(adict):
        composite = [adict[k] for k in keynames]
        for i, (k, v) in enumerate(zip(keynames, composite)):
            if k in negate:
                composite[i] = -v
        return composite
    return getit

sort = sorted(chars, key=sortkeypicker(['y', 'x']))

flag = ""
for x in sort:
    if x['x'] > 0:
        flag += x['char']

print(flag)
