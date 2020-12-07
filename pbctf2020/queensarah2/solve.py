#!/usr/bin/python

from string import ascii_lowercase
import math
import sys

from pwn import *

from p_square_root import square_roots

p = remote("queensarah2.chal.perfect.blue", 1)
#p = process("./challenge.py")
ALPHABET = ascii_lowercase + "_"

p.recvline()
enc_flag = p.recvline().decode().strip()[2:-2]
log.info("encrypted flag: " + enc_flag)

canary_plaintext = "this_is_a_str_"
assert(len(canary_plaintext) % 2 == 0)
p.sendlineafter("> ", canary_plaintext)
p.recvline()
canary_enctext = p.recvline().decode().strip()
log.info("encrypted canary: " + canary_enctext)

# encryption works like this:
# each 2 chars gets subbed from sbox
# then, message is set to each even char (i=0,2,4...)
# and then each odd char (i=1,3,5...)

# leak sbox
# if we send two chars, it does two rounds
# so, we know m and c2
# m => c1 => c2
double_sbox = {}

log.info("leaking double sbox")

for i in range(len(ALPHABET)):
    for j in range(len(ALPHABET)):
        k = ALPHABET[i] + ALPHABET[j]
        p.sendlineafter("> ", k)
        p.recvline()
        double_sbox[k] = p.recvline().decode().strip()

log.info("got double sbox, aa => " + double_sbox["aa"])

##### MAGIC SAGE CODE FROM TEAMMATE #####
# if num possibility > 10k, retry
log.info("computing square roots")
p_sq = []
double_sbox_keys = list(double_sbox.keys()) # equivalent to the list of bigrams: aa, ab, ..., _z, __

for i in range(len(double_sbox_keys)):
    p_sq.append(double_sbox_keys.index(double_sbox[double_sbox_keys[i]]))

assert(len(p_sq) == 27**2)

roots = square_roots(p_sq)
log.info("got square roots, identifying proper permutation")

def decrypt_msg(sbox, enctext):
    def unshuffle(message):
        out = []
        mid = len(message)//2
        [out.extend(x) for x in zip(message[:mid], message[mid:])]
        return out
    
    def decrypt(sbox, message):
        out = []
        sbox_keys = list(sbox.keys())
        sbox_vals = list(sbox.values())
    
        for i in range(0, len(message), 2):
            out.extend(sbox_keys[sbox_vals.index("".join(message[i:i+2]))])
    
        return out

    rounds = int(2 * math.ceil(math.log(len(enctext), 2))) 
    message = list(enctext)

    for r in range(rounds):
        if r != 0:
            message = unshuffle(message)
    
        message = decrypt(sbox, message)

    return "".join(message)

# identify which root works
for root in roots:
    assert(len(root) == 27**2)

    # build sbox
    sbox = {}
    for i in range(len(root)):
        sbox[double_sbox_keys[i]] = double_sbox_keys[root[i]]

    assert(len(sbox.keys()) == 27**2)
    
    #log.info("aa => " + sbox["aa"] + " => " + double_sbox["aa"] + ", " + sbox[sbox["aa"]] + " should equal " + double_sbox["aa"])

    # decrypt canary
    test_decrypt = decrypt_msg(sbox, canary_enctext)
    if test_decrypt == canary_plaintext:
        log.info("found the right roots, built the sbox")
        break
else:
    log.error("failed to decrypt canary")
    sys.exit(1)

log.info("decrypting flag")

# decrypt flag with sbox
flag = "pbctf{" + decrypt_msg(sbox, enc_flag) + "}"
log.info("flag: " + flag)
