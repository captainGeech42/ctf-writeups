#!/usr/bin/env python3

# https://stackoverflow.com/a/7397689
import binascii

def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return int2bytes(n).decode(encoding, errors)

def int2bytes(i):
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))

scramble1 = "B2 R U F' R' L' B B2 L F D D' R' F2 D' R R D2 B' L R"
scramble2 = "L' L B F2 R2 F2 R' L F' B' R D' D' F U2 B' U U D' U2 F'"
scramble3 = "L F' F2 R B R R F2 F' R2 D F' U L U' U' U F D F2 U R U' F U B2 B U2 D B F2 D2 L2 L2 B' F' D' L2 D U2 U2 D2 U B' F D R2 U2 R' B' F2 D' D B' U B' D B' F' U' R U U' L' L' U2 F2 R R F L2 B2 L2 B B' D R R' U L"

base9_lookup = {
    "L": 0,
    "F": 0,
    "R": 1,
    "B": 1,
    "U": 2,
    "L2": 2,
    "D": 3,
    "R2": 3,
    "F2": 4,
    "U2": 4,
    "B2": 5,
    "D2": 5,
    "L'": 6,
    "F'": 6,
    "R'": 7,
    "U'": 7,
    "B'": 8,
    "D'": 8
}

# step 1: get P
print("=== Scramble 1 ===")

h_1_9 = ""
for n in scramble1.split(" "):
    h_1_9 += str(base9_lookup[n])
print("h_1,9 = {}".format(h_1_9))

h_1_10 = str(int(h_1_9, 9))
print("h_1,10 = {}".format(h_1_10))

i = int(h_1_10[0])
print("i = {}".format(i))

P = str(h_1_10[i+1:i+10])
print("P = {}".format(P))

# step 1.5: build new encoding table
new_lookup = {}
x = 0
for y in P:
    for z in base9_lookup.keys():
        if base9_lookup[z] == int(y):
            new_lookup[z] = x
    x += 1
print()
print("New encoding table:")
print(repr(new_lookup))

# step 2: get len_m
print()
print("=== Scramble 2 ===")

h_2_9 = ""
for n in scramble2.split(" "):
    h_2_9 += str(new_lookup[n])
print("h_2_9 = {}".format(h_2_9))

h_2_10 = str(int(h_2_9, 9))
print("h_2_10 = {}".format(h_2_10))

j = int(h_2_10[0])
print("j = {}".format(j))

k = int(h_2_10[1])
print("k = {}".format(k))

len_m = int(h_2_10[2+j:2+j+k])
print("len_m = {}".format(len_m))

# step 3: get message
print()
print("=== Scramble 3 ===")

m_9 = ""
for n in scramble3.split(" ")[:len_m]:
    m_9 += str(new_lookup[n])
print("m_9 = {}".format(m_9))

m_10 = int(m_9, 9)
print("m_10 = {}".format(m_10))

m_2 = bin(m_10)
print("m_2 = {}".format(m_2))

flag = str(text_from_bits(m_2))
print("flag = {}".format(flag))
