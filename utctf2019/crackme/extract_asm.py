#!/usr/bin/env python

from capstone import *

with open("newstuff.bin", "rb") as f:
    stuff = f.read()

md = Cs(CS_ARCH_X86, CS_MODE_64)
for i in md.disasm(stuff, 0x1000):
        print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
