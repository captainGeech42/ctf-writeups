from binaryninja.log import log_info, log_error
from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import InstructionTextTokenType, Endianness, BranchType
from enum import Enum, auto

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

    return (Opcode(opcode), rx, ry, rz)

def parse_comparison(data):
    assert(len(data) == 3)

    #  5     3    5     3    8        = 24 bits
    # |*****|*** |*****|*** |********
    #  opcode     rx         ry/imm8
    #        unused     unused
    # spaces == byte boundary

    opcode = data[0] >> 3
    rx = data[1] >> 3
    ry = data[2]

    return (Opcode(opcode), rx, ry)

def parse_control_flow(data):
    assert(len(data) == 3)
    
    #  5     3    16                = 24 bits
    # |*****|*** |****************|
    #  opcode     imm16
    #        unused
    # spaces == byte boundary

    opcode = data[0] >> 3
    imm = btoi(data[1:])

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
    imm = data[1] & 0x7

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
            log_error(f"invalid opcode requested in OpcodeType.get(): {str(opcode)}")
            return None

class ARC6969(Architecture):
    name = "arc6969"
    address_size = 2
    default_int_size = 1
    instr_alignment = 1
    max_instr_length = 3
    endianness = Endianness.BigEndian

    regs = {
        # 32 8bit GP regs
        "r0": RegisterInfo("r0", 1),
        "r1": RegisterInfo("r1", 1),
        "r2": RegisterInfo("r2", 1),
        "r3": RegisterInfo("r3", 1),
        "r4": RegisterInfo("r4", 1),
        "r5": RegisterInfo("r5", 1),
        "r6": RegisterInfo("r6", 1),
        "r7": RegisterInfo("r7", 1),
        "r8": RegisterInfo("r8", 1),
        "r9": RegisterInfo("r9", 1),
        "r10": RegisterInfo("r10", 1),
        "r11": RegisterInfo("r11", 1),
        "r12": RegisterInfo("r12", 1),
        "r13": RegisterInfo("r13", 1),
        "r14": RegisterInfo("r14", 1),
        "r15": RegisterInfo("r15", 1),
        "r16": RegisterInfo("r16", 1),
        "r17": RegisterInfo("r17", 1),
        "r18": RegisterInfo("r18", 1),
        "r19": RegisterInfo("r19", 1),
        "r20": RegisterInfo("r20", 1),
        "r21": RegisterInfo("r21", 1),
        "r22": RegisterInfo("r22", 1),
        "r23": RegisterInfo("r23", 1),
        "r24": RegisterInfo("r24", 1),
        "r25": RegisterInfo("r25", 1),
        "r26": RegisterInfo("r26", 1),
        "r27": RegisterInfo("r27", 1),
        "r28": RegisterInfo("r28", 1),
        "r29": RegisterInfo("r29", 1),
        "r30": RegisterInfo("r30", 1),
        "r31": RegisterInfo("r31", 1),

        # PC
        "pc": RegisterInfo("pc", 2),

        # flags
        # bit0 = zf
        # bit1 = cf
        # bit2 = sf
        # bit3 = of
        # high bits unused
        "flags": RegisterInfo("flags", 1)
    }

    def get_instruction_info(self, data, addr):
        try:
            opcode = Opcode(data[0] >> 3)
        except ValueError:
            # invalid opcode, probably data or something
            return None
        
        t = OpcodeType.get(opcode)
        assert(t is not None)

        result = InstructionInfo()

        if t == OpcodeType.IO:
            result.length = 2
        else:
            result.length = 3

        if t == OpcodeType.CF:
            if opcode == Opcode.RET or opcode == Opcode.HALT:
                result.add_branch(BranchType.FunctionReturn)
                result.length = 1
            else:
                _, imm = parse_control_flow(data[:result.length])
                if opcode == Opcode.CALL:
                    result.add_branch(BranchType.CallDestination, imm)
                elif opcode == Opcode.RET or opcode == Opcode.HALT:
                    result.add_branch(BranchType.FunctionReturn)
                elif opcode == Opcode.JMP:
                    result.add_branch(BranchType.UnconditionalBranch)
                elif opcode in [Opcode.JE, Opcode.JNE, Opcode.JB, Opcode.JL, Opcode.JG, Opcode.JA]:
                    result.add_branch(BranchType.TrueBranch, imm)
                    result.add_branch(BranchType.FalseBranch, addr + result.length)
                else:
                    log_error(f"unhandled control flow instruction at {hex(addr)}: {str(opcode)}")
        
        return result

    def get_instruction_text(self, data, addr):
        result = []

        try:
            opcode = Opcode(data[0] >> 3)
        except ValueError:
            # invalid opcode, probably data or something
            return None

        t = OpcodeType.get(opcode)
        assert(t is not None)

        if t == OpcodeType.IO:
            data = data[:2]
            length = 2
        else:
            data = data[:3]
            length = 3

        result.append(InstructionTextToken(InstructionTextTokenType.InstructionToken, str(opcode)))

        if opcode not in [Opcode.RET, Opcode.HALT]:
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
        else:
            # only one byte for HALT, idk about RET but probably
            length = 1

        if t == OpcodeType.MATH:
            _, rx, ry, rz = parse_arithmetic(data)
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"r{rx}"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, ", "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"r{ry}"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, ", "))

            if opcode in [Opcode.ADD, Opcode.SUB, Opcode.OR, Opcode.XOR, Opcode.AND, Opcode.SHL, Opcode.SHR]:
                result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"r{rz}"))
            else:
                # rz == imm8 now
                result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(rz), rz))
        
        elif t == OpcodeType.CMP:
            _, rx, ry = parse_comparison(data)
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"r{rx}"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, ", "))

            if opcode == Opcode.CMP:
                result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"r{ry}"))
            else:
                # ry == imm8 now
                result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(ry), ry))

        elif t == OpcodeType.CF:
            if opcode != Opcode.RET and opcode != Opcode.HALT:
                _, imm = parse_control_flow(data)

                result.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(imm), imm))

        elif t == OpcodeType.MEM:
            _, rx, ry, rz = parse_mem_op(data)
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"r{rx}"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, ", "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"r{ry}"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, ", "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"r{rz}"))

        elif t == OpcodeType.IO:
            _, rx, imm = parse_io_comm(data)

            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"r{rx}"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, ", "))
            result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, hex(imm), imm))

        else:
            log_error(f"unknown opcode type in get_instruction_text() at {hex(addr)}: {str(t)}")

        return result, length

    def get_instruction_low_level_il(self, data, addr, il):
        return None

ARC6969.register()