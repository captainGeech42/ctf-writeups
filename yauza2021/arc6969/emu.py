#!/usr/bin/env python3

from enum import Enum, auto
import sys

from fixedint import UInt8, UInt16 # pip install fixedint

# big endian bytes to int
btoi = lambda x: int.from_bytes(x, byteorder="big")

def parse_arithmetic(data):
    assert(len(data) == 3)

    #  5     1 5      5       8        = 24 bits
    # |*****|*|** ***|***** |********|
    #  opcode  rx     ry     imm8/rz
    #        unused
    # 0x1f == 11111b
    # spaces == byte boundary

    opcode = data[0] >> 3
    rx = btoi(data[:2]) >> 5 & 0x1f
    ry = data[1] & 0x1f
    rz = data[2]

    return (Opcode(opcode), rx, ry, UInt8(rz))

def parse_comparison(data):
    assert(len(data) == 3)

    #  5     3    5     3    8        = 24 bits
    # |*****|*** |*****|*** |********
    #  opcode     rx         ry/imm8
    #        unused     unused
    # spaces == byte boundary

    opcode = data[0] >> 3
    rx = data[1] >> 3
    ry = UInt8(data[2])

    return (Opcode(opcode), rx, ry)

def parse_control_flow(data):
    assert(len(data) == 3)
    
    #  5     3    16                 = 24 bits
    # |*****|*** |******** ********|
    #  opcode     imm16
    #        unused
    # spaces == byte boundary

    opcode = data[0] >> 3
    imm = UInt16(btoi(data[1:]))

    return (Opcode(opcode), imm)

def parse_mem_op(data):
    assert(len(data) == 3)

    #  5     1 5      5      3   5      = 24 bits
    # |*****|*|** ***|*****| ***|*****|
    #  opcode  rx     ry         rz
    #        unused          unused
    # 0x1f == 11111b
    # spaces == byte boundary

    opcode = data[0] >> 3
    rx = btoi(data[:2]) >> 5 & 0x1f
    ry = data[1] & 0x1f
    rz = data[2] & 0x1f

    return (Opcode(opcode), rx, ry, rz)

def parse_io_comm(data):
    assert(len(data) == 2)

    #  5     3    5     3    = 16 bits
    # |*****|*** |*****|***|
    #  opcode     rx    imm
    #        unused
    # 0x7 == 111b
    # spaces == byte boundary

    opcode = data[0] >> 3
    rx = data[1] >> 3
    imm = IoDevice(data[1] & 0x7)

    return (Opcode(opcode), rx, imm)

class Opcode(Enum):
    # arithmetic
    ADD = 0
    ADDI = 1
    SUB = 2
    SUBI = 3
    OR = 6
    ORI = 7
    XOR = 8
    XORI = 9
    AND = 10
    ANDI = 11
    SHL = 12
    SHR = 13

    # comparison
    CMP = 4
    CMPI = 5

    # control flow
    CALL = 24
    RET = 25
    JMP = 16
    JE = 17
    JNE = 18
    JB = 19
    JL = 20
    JG = 26
    JA = 27
    HALT = 23

    # mem ops
    RD = 14
    WR = 15

    # io
    IO = 21

    def __str__(self):
        return self.name.lower()

class OpcodeType(Enum):
    MATH = auto()
    CMP = auto()
    CF = auto()
    MEM = auto()
    IO = auto()

    @classmethod
    def get(cls, opcode):
        if opcode in [Opcode(x) for x in [0,1,2,3,6,7,8,9,10,11,12,13]]:
            return cls.MATH
        elif opcode in [Opcode(x) for x in [4,5]]:
            return cls.CMP
        elif opcode in [Opcode(x) for x in [24,25,16,17,18,19,20,26,27,23]]:
            return cls.CF
        elif opcode in [Opcode(x) for x in [14,15]]:
            return cls.MEM
        elif opcode == Opcode.IO:
            return cls.IO
        else:
            print(f"invalid opcode requested in OpcodeType.get(): {str(opcode)}")
            return None

class Flags(Enum):
    ZF = 1 << 0
    CF = 1 << 1
    SF = 1 << 2
    OF = 1 << 3

class IoDevice(Enum):
    IO_GPU_SET_X = 1
    IO_GPU_SET_Y = 2
    IO_GPU_DRAW = 3
    IO_GPU_UPDATE = 4
    IO_SERIAL_LENGTH = 5
    IO_SERIAL_READ = 6
    IO_SERIAL_WRITE = 7

class Emulator():
    def __init__(self, rom: bytes):
        # r0-r31
        self.regs = [UInt8(0)] * 32

        self.pc = UInt16(0)

        # bit0 = zf
        # bit1 = cf
        # bit2 = sf
        # bit3 = of
        # high bits unused
        self.flags = UInt8(0)

        self.mem = [UInt8(x) for x in list(rom)]
        self.mem += [UInt8(0)] * (0x10000 - len(rom))

        self.serial_buf = b""

        assert(len(self.mem) == 0x10000)

    def run(self):
        while True:
            opcode = Opcode(self.mem[self.pc] >> 3)

            t = OpcodeType.get(opcode)
            assert(t is not None)

            if t == OpcodeType.IO:
                data = bytes(self.mem[self.pc:self.pc+2])
                self.pc += 2
            else:
                data = bytes(self.mem[self.pc:self.pc+3])
                self.pc += 3

            if t == OpcodeType.MATH:
                _, a1, a2, a3 = parse_arithmetic(data)

                if opcode == Opcode.ADD:
                    self.regs[a1] = self.regs[a2] + self.regs[a3]
                elif opcode == Opcode.ADDI:
                    self.regs[a1] = self.regs[a2] + a3
                elif opcode == Opcode.SUB:
                    self.regs[a1] = self.regs[a2] - self.regs[a3]
                elif opcode == Opcode.SUBI:
                    self.regs[a1] = self.regs[a2] - a3
                elif opcode == Opcode.OR:
                    self.regs[a1] = self.regs[a2] | self.regs[a3]
                elif opcode == Opcode.ORI:
                    self.regs[a1] = self.regs[a2] | a3
                elif opcode == Opcode.XOR:
                    self.regs[a1] = self.regs[a2] ^ self.regs[a3]
                elif opcode == Opcode.XORI:
                    self.regs[a1] = self.regs[a2] ^ a3
                elif opcode == Opcode.AND:
                    self.regs[a1] = self.regs[a2] & self.regs[a3]
                elif opcode == Opcode.ANDI:
                    self.regs[a1] = self.regs[a2] & a3
                elif opcode == Opcode.SHL:
                    self.regs[a1] = self.regs[a2] << self.regs[a3]
                elif opcode == Opcode.SHR:
                    self.regs[a1] = self.regs[a2] >> self.regs[a3]
                else:
                    print(f"invalid OpcodeType.MATH opcode: {opcode}")
                    break
            
            elif t == OpcodeType.CMP:
                _, a1, a2 = parse_comparison(data)

                if opcode == Opcode.CMP:
                    val = self.regs[a2]
                elif opcode == Opcode.CMPI:
                    val = a2
                else:
                    print(f"invalid OpcodeType.CMP opcode: {opcode}")
                    break

                self.flags ^= self.flags
                
                if self.regs[a1] == val:
                    self.flags |= Flags.ZF.value
                if val > self.regs[a1]:
                    self.flags |= Flags.CF.value
                if int(self.regs[a1]) - int(val) < 0:
                    self.flags |= Flags.SF.value
                if (int(self.regs[a1]) + val) % 256 != 0:
                    self.flags |= Flags.OF.value

            elif t == OpcodeType.CF:
                if opcode == Opcode.RET:
                    self.pc == self.regs[31]
                elif opcode == Opcode.HALT:
                    print("<halt>")
                    break
                else:
                    _, imm = parse_control_flow(data)

                    if opcode == Opcode.CALL:
                        self.regs[31] = self.pc
                        self.pc = imm
                    elif opcode == Opcode.JMP:
                        self.pc = imm
                    elif opcode == Opcode.JE and self.flags & Flags.ZF.value == 1:
                        self.pc = imm
                    elif opcode == Opcode.JNE and self.flags & Flags.ZF.value == 0:
                        self.pc = imm
                    elif opcode == Opcode.JB and self.flags & Flags.CF.value == 1:
                        self.pc = imm
                    elif opcode == Opcode.JL and (self.flags & Flags.SF.value) != (self.flags & Flags.OF.value):
                        # self.pc = imm
                        pass
                    elif opcode == Opcode.JG and self.flags & Flags.ZF.value == 0 and self.flags & Flags.SF.value == self.flags & Flags.OF.value:
                        self.pc = imm
                    elif opcode == Opcode.JA and self.flags & Flags.CF.value == 0 and self.flags & Flags.ZF.value == 0:
                        self.pc = imm
                    # elif opcode == Opcode.JL:
                    #     # cheating
                    #     self.pc = imm
                    else:
                        # assume we handle all opcodes and conditions just weren't met
                        pass
            
            elif t == OpcodeType.MEM:
                _, a1, a2, a3 = parse_mem_op(data)

                if opcode == Opcode.RD:
                    offset = UInt16(self.regs[a2] << 8 | self.regs[a3])
                    self.regs[a1] = self.mem[offset]
                elif opcode == Opcode.WR:
                    offset = UInt16(self.regs[a2] << 8 | self.regs[a3])
                    self.mem[offset] = self.regs[a1]
                else:
                    print(f"invalid OpcodeType.MEM opcode: {opcode}")
                    break
            
            elif t == OpcodeType.IO:
                _, a1, a2 = parse_io_comm(data)

                if opcode != Opcode.IO:
                    print(f"invalid OpcodeType.IO opcode: {opcode}")
                    break

                if a2 == IoDevice.IO_SERIAL_LENGTH:
                    # print("IO_SERIAL_LENGTH", flush=True)
                    # cheat
                    self.regs[a1] = UInt8(0x20)
                elif a2 == IoDevice.IO_SERIAL_READ:
                    # print("reading", flush=True)
                    # if len(self.serial_buf) == 0:
                    #     self.serial_buf = sys.stdin.read()

                    # self.regs[a1] = UInt8(self.serial_buf[0])
                    # self.serial_buf = self.serial_buf[1:]
                    self.regs[a1] = sys.stdin.read(1)
                elif a2 == IoDevice.IO_SERIAL_WRITE:
                    sys.stdout.write(chr(self.regs[a1]))
                    sys.stdout.flush()
                else:
                    print(f"unsuppored IoDevice call: {a2}")
                    break

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