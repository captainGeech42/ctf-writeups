#!/usr/bin/env python3

import hashlib

charset = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*()-=_+[]\|;':\",./<>?"

def verifier0():
    encrypted = [50,48,45,50,42,39,54,49]
    word = ""
    for e in encrypted:
        word += chr(e ^ 0x42)
    return word

def verifier1():
    encrypted = [115,117,111,105,120,110,97]
    word = ""
    for i in range(len(encrypted)):
        word += chr(encrypted[len(encrypted) - 1 - i])
    return word

def verifier2():
    def java_string_hashcode(s):
        h = 0
        for c in s:
            h = (31 * h + ord(c)) & 0xFFFFFFFF
        return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000

    encrypted = [3080674, 3110465, 3348793, 3408375, 3319002, 3229629, 3557330, 3229629, 3408375, 3378584]
    word = ""
    for e in encrypted:
        for c in charset:
            if java_string_hashcode(c+"foo") == e:
                word += c
                break
    return word

def verifier3():
    encrypted = "obwaohfcbwq"
    word = ""
    for e in encrypted:
        word += chr(((ord(e) - ord('a') - 12)) + ord('a'))

    # return word
    # https://www.rot13.com/
    # do rot12
    return "animatronic"

def verifier4():
    encrypted = [3376, 3295, 3646, 3187, 3484, 3268]
    word = ""
    for e in encrypted:
        for c in charset:
            if ord(c) * int("033", 8) + 568 == e:
                word += c
                break
    return word

def verifier5():
    encrypted = "8FA14CDD754F91CC6554C9E71929CCE7865C0C0B4AB0E063E5CAA3387C1A8741FBADE9E36A3F36D3D676C1B808451DD7FBADE9E36A3F36D3D676C1B808451DD7"
    word = ""
    while len(encrypted) != 0:
        for c in charset:
            digest = hashlib.md5(c.encode('utf-8')).hexdigest().upper()
            if encrypted[:len(digest)] == digest:
                word += c
                encrypted = encrypted[len(digest):]
                break
    return word

# or just look it up on https://crackstation.net/
# it's "stop"
def verifier6():
    encrypted = "1B480158E1F30E0B6CEE7813E9ECF094BD6B3745"
    options = []
    for c in charset:
        for d in charset:
            for e in charset:
                for f in charset:
                    options.append("{}{}{}{}".format(c,d,e,f))
    for o in options:
        if hashlib.sha1(o.encode('utf-8')).hexdigest().upper() == encrypted:
            return o

def verifier7():
    return "goodbye"

def main():
    words = []
    words.append(verifier0())
    words.append(verifier1())
    words.append(verifier2())
    words.append(verifier3())
    words.append(verifier4())
    words.append(verifier5())
    words.append(verifier6())
    words.append(verifier7())
    
    for x in range(8-len(words)):
        words.append("asdf")

    for x in range(len(words)):
        if words[x] == "asdf":
            break
        print("Verifier {}: {}".format(x, words[x]))

    flag = "utflag{" + "_".join(words) + "}"
    print("Flag: {}".format(flag))

if __name__ == "__main__":
    main()