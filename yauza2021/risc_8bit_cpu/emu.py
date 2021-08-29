#!/usr/bin/env python3

import sys
import traceback

from fixedint import UInt8, UInt16 # pip install fixedint

# big endian bytes to int
btoi = lambda x: int.from_bytes(x, byteorder="big")

class Emulator():

    def __init__(self, image: bytes):
        # R1, R2, R3 (aka A, B, C)
        self.regs = [UInt8(0), UInt8(0), UInt8(0)]
        self.flag = 0

        self.pc = UInt16(0x1000)

        self.mem = [UInt8(x) for x in list(image)]
        self.mem += [UInt8(0)] * (0x10000 - len(image))

        assert(len(self.mem) == 0x10000)

    def run(self):
        while self._exec_inst():
            pass

        with open("mem.bin", "wb") as f:
            f.write(bytes(self.mem))
        
        print("regs: " + ", ".join([hex(x) for x in self.regs]))
        print("pc: " + hex(self.pc))

    def _exec_inst(self):
        # yay RISC
        try:
            data = bytes(self.mem[self.pc:self.pc+4])
            self.pc += 4
        except:
            print(self.mem[self.pc:self.pc+4])
            return

        reg_taint = False
        try:
            if data[0] == 0x0:
                # ADD
                self.regs[data[1]] += data[3]
                reg_taint = True
            elif data[0] == 0x1:
                # XOR
                self.regs[data[1]] ^= data[3]
                reg_taint = True
            elif data[0] == 0x2:
                # AND
                self.regs[data[1]] &= data[3]
                reg_taint = True
            elif data[0] == 0x3:
                # OR
                self.regs[data[1]] |= data[3]
                reg_taint = True
            elif data[0] == 0x4:
                # LD
                self.regs[data[1]] = data[3]
                reg_taint = True
            elif data[0] == 0x5:
                self.regs[data[1]] = self.regs[data[3]]
                reg_taint = True
            elif data[0] == 0x6:
                self.regs[data[1]] = self.mem[btoi(data[2:])]
                reg_taint = True
            elif data[0] == 0x7:
                offset = UInt16((self.regs[1] << 8) + self.regs[2])
                # print(f"offset: {hex(offset)}")
                self.regs[data[1]] = self.mem[offset]
                reg_taint = True
            elif data[0] == 0x8:
                self.mem[btoi(data[2:])] = self.regs[data[1]]
            elif data[0] == 0x9:
                offset = UInt16((self.regs[1] << 8) + self.regs[2])
                self.mem[offset] = self.regs[data[1]]
            elif data[0] == 0xa:
                print(chr(self.regs[data[1]]), end="")
            elif data[0] == 0xb:
                self.pc = btoi(data[2:])
            # admin said in discord that conditional jump dest addrs are off by four
            elif data[0] == 0xc:
                if not self.flag:
                    self.pc = btoi(data[2:]) + 4
            elif data[0] == 0xd:
                if self.flag:
                    self.pc = btoi(data[2:]) + 4
            elif data[0] == 0xe:
                self.flag = self.regs[data[1]] == data[3]
            elif data == b"\x44\x44\x44\x44":
                return False
            elif data == b"\x33\x33\x33\x33":
                pass
            else:
                print(f"bad opcodes: {repr(data)}")
                return False
        except Exception as e:
            print(f"error: {repr(data)}")
            traceback.print_exc()
            return False

        # trunc regs
        if reg_taint:
            for x in range(3):
                self.regs[x] &= 0xff

        return True

def main(argv):
    try:
        rom_path = argv[1]
    except IndexError:
        sys.stderr.write(f"usage: {argv[0]} [path to rom file]\n")
        return 2

    with open(rom_path, "rb") as f:
        emu = Emulator(f.read())

    emu.run()

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))