from binaryninja.log import log_info, log_error
from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import InstructionTextTokenType, Endianness, BranchType

# https://binary.ninja/2020/01/08/guide-to-architecture-plugins-part1.html

class SFT0(Architecture):
    name = "sft0"
    address_size = 2
    default_int_size = 1
    instr_alignment = 0 # i think this means they are aligned?
    max_instr_length = 4 # 4 byte instructions
    endianness = Endianness.BigEndian

    regs = {
        # general purpose 1 byte regs
        "R0": RegisterInfo("R0", 1),
        "R1": RegisterInfo("R1", 1),
        "R2": RegisterInfo("R2", 1),

        # program counter
        "PC": RegisterInfo("PC", 2),

        # 1 bit flag register, idk
        "FLAG": RegisterInfo("FLAG", 1)
    }

    def get_instruction_info(self, data, addr):
        result = InstructionInfo()
        result.length = 4

        if data[0] == 0xb:
            # JMP KKKK
            result.add_branch(BranchType.UnconditionalBranch, int.from_bytes(data[2:], "big"))
        elif data[0] == 0xc or data[0] == 0xd:
            # JNZ KKKK or JZ KKKK
            result.add_branch(BranchType.TrueBranch, int.from_bytes(data[2:], "big"))
            result.add_branch(BranchType.FalseBranch, addr + 4)
        elif data == b"\x44\x44\x44\x44":
            result.add_branch(BranchType.FunctionReturn)

        return result

    def get_instruction_text(self, data, addr):
        result = []

        if data[0] == 0x0:
            # ADD Rx, KK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "ADD"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ","))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, str(data[3]), data[3]))
        elif data[0] == 0x1:
            # XOR Rx, KK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "XOR"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ","))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, str(data[3]), data[3]))
        elif data[0] == 0x2:
            # AND Rx, KK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "AND"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ","))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, str(data[3]), data[3]))
        elif data[0] == 0x3:
            # OR Rx, KK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "OR"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ","))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, str(data[3]), data[3]))
        elif data[0] == 0x4:
            # LD Rx, KK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "LD"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ","))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, str(data[3]), data[3]))
        elif data[0] == 0x5:
            # MOV Rx, Ry
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "MOV"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ","))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[3]}"))
        elif data[0] == 0x6:
            # LDR Rx, KKKK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "LDR"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ","))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(int.from_bytes(data[2:], "big")), int.from_bytes(data[2:], "big")))
        elif data[0] == 0x7:
            # LDR Rx
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "LDR"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
        elif data[0] == 0x8:
            # STR Rx, KKKK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "STR"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ","))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(int.from_bytes(data[2:], "big")), int.from_bytes(data[2:], "big")))
        elif data[0] == 0x9:
            # STR Rx
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "STR"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
        elif data[0] == 0xa:
            # PUT Rx
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "PUT"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
        elif data[0] == 0xb:
            # JMP KKKK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "JMP"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(int.from_bytes(data[2:], "big")), int.from_bytes(data[2:], "big")))
        elif data[0] == 0xc:
            # JNZ KKKK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "JNZ"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(int.from_bytes(data[2:], "big")), int.from_bytes(data[2:], "big")))
        elif data[0] == 0xd:
            # JZ KKKK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "JZ"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.PossibleAddressToken, hex(int.from_bytes(data[2:], "big")), int.from_bytes(data[2:], "big")))
        elif data[0] == 0xe:
            # CMPEQ Rx, KK
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "CMPEQ"))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"R{data[1]}"))
            result.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ","))
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, " "))
            result.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, str(data[3]), data[3]))
        elif data == b"\x44\x44\x44\x44":
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "HLT"))
        elif data == b"\x33\x33\x33\x33":
            result.append(InstructionTextToken(InstructionTextTokenType.TextToken, "NOP"))
        else:
            log_error(f"couldn't parse instruction: {data}")

        return result, 4

    def get_instruction_low_level_il(self, data, addr, il):
        return None

SFT0.register()