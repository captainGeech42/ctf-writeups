#!/usr/bin/env python

import base64
import hashlib

from Crypto.Cipher import AES
from z3 import *

password = [BitVec(f"password_{i}", 8) for i in range(26)]

s = Solver()

def toUpper(chrs):
    out = []
    for i in chrs:
        out.append(i-0x20)
    return out

s.add(password[0] == ord("l"))
s.add(password[1] + password[2] == 217)
s.add(password[0] ^ password[2] == 24)
s.add(password[1] ^ password[3] == ord(":"))
s.add(password[3] == password[6])
s.add(password[6] - ord("1") == password[9])
s.add(password[4] ^ ord("m") == 0)
s.add(password[5] + 8 == password[4])
s.add((password[9] * 5) + (password[6] * 9) == 1085)
s.add((password[6] * 8) - (password[7] * 3) == 445)
s.add(password[10] == password[0])
s.add(password[11] + 4 == 55)

s.add(password[11] ^ password[12] == 0)
s.add(password[2] == password[13])
s.add(password[4] == password[15])
s.add(password[16] == password[12])
s.add(password[14] == password[6])
s.add(password[17] == password[14])

a = toUpper(password[7:9]) # substring(7,9).toUpper()
s.add(password[18] == a[0])
s.add(password[19] == a[1])

s.add(password[20] * 9 == 297)
s.add(password[20] == password[21])
s.add(password[21] == password[22])

s.add(password[20] == password[23])
s.add(password[21] == password[24])
s.add(password[22] == password[25])

s.add(password[8] * 1337 == 147070)

s.check()
model = s.model()

key = ""
for p in password:
    try:
        key += chr(model[p].as_long())
    except AttributeError:
        pass

print(key)

h = hashlib.sha1()
h.update(key.encode())
secretkey = h.digest()[:16]

cipher = AES.new(secretkey, AES.MODE_ECB)
flag = cipher.decrypt(base64.b64decode("e+aJggifvYOZCTlZKy6uVkuzqTnkJY4JCE45IG0vVIcK8D7+Smv5qqKpgfhuRuL3"))

print(flag.decode().strip())
