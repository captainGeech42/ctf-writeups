#!/usr/bin/env python

from pwn import *
from time import sleep
from base64 import b64encode, b64decode
from capstone import *
import sys

def init():
    p = remote("13.231.83.89", 30262)
    for x in range(3):
        p.sendline()
    p.sendline("A")
    p.sendline()
    p.sendline("B")
    for x in range(2):
        p.sendline()
  
    sleep(5)

    return p

def enter_room(p, i):
    log.info("Going to room #{}".format(i+1))

    if i == 0:
        for x in range(5):
            log.info("...")
            p.sendline("w")
            sleep(1)
    elif i == 1:
        for x in range(15):
            log.info("...")
            p.sendline("a")
            sleep(1)
        log.info("...")
        p.sendline("w")
        sleep(1)
    elif i == 2:
        for x in range(5):
            log.info("...")
            p.sendline("d")
            sleep(1)
        for x in range(4):
            log.info("...")
            p.sendline("s")
            sleep(1)
        log.info("...")
        p.sendline("a")
        sleep(1)
    elif i == 3:
        for x in range(4):
            log.info("...")
            p.sendline("s")
            sleep(1)
        for x in range(5):
            log.info("...")
            p.sendline("d")
            sleep(1)
        log.info("...")
        p.sendline("s")
        sleep(1)
    elif i == 4:
        for x in range(15):
            log.info("...")
            p.sendline("a")
            sleep(1)
        log.info("...")
        p.sendline("s")
        sleep(1)
    elif i == 5:
        for x in range(16):
            log.info("...")
            p.sendline("a")
            sleep(1)
        log.info("...")
        p.sendline("s")
        sleep(1)
    elif i == 6:
        for x in range(9):
            log.info("...")
            p.sendline("w")
            sleep(1)
    else:
        log.failure("Invalid room # (i={})".format(i))
        sys.exit(1)

# Stage 1
def get_asm(p):
    p.sendline()

    p.recvuntil("Give me the binary code of the following assembly ( in base64 encoded format ):")
    p.recvline()

    code = p.recvuntil("Answer:")
    print code

    code = code[:-8]
    log.info("Got {} lines of asm from remote".format(len(code.split("\n"))))
    return code

def set_arch(code):
    if "esp" in code:
        context.arch = "i386"
        context.endianness = "little"
    elif "rsp" in code:
        context.arch = "amd64"
        context.endianness = "little"
    elif "w8" in code:
        context.arch = "aarch64"
        context.endianness = "little"
    elif "r0" in code:
        context.arch = "arm"
        context.endianness = "little"
    elif "stwu" in code:
        context.arch = "ppc32"
        context.endianness = "big"
    elif "$sp" in code:
        context.arch = "mips"
        context.endianness = "big"
    else:
        log.failure("Couldn't identify arch, exiting")
        sys.exit(1)

    log.info("Arch is " + context.arch)

def get_opcode(p):
    p.recvline()
    x = p.recvline()
    log.info("Got {} opcodes from remote".format(len(x)))
    return x

def opcode_to_code(ops, b64=True):
    if b64:
        ops = b64decode(ops)

    if context.arch == "i386":
        md = Cs(CS_ARCH_X86, CS_MODE_32)
    elif context.arch == "amd64":
        md = Cs(CS_ARCH_X86, CS_MODE_64)
    elif context.arch == "aarch64":
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    elif context.arch == "arm":
        md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    elif context.arch == "powerpc":
        md = Cs(CS_ARCH_PPC, CS_MODE_32 + CS_MODE_BIG_ENDIAN)
    elif context.arch == "mips":
        md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN)
    else:
        log.failure("Invalid arch/mode")
        sys.exit(1)

    output = ""
    for call in md.disasm(ops, 0x1000):
        output += "{} {}\n".format(call.mnemonic, call.op_str)

    log.info("Generated {} lines of asm".format(len(output.split("\n"))))

    if context.arch == "arm":
        return output[:-1]
    else:
        return output[:-2]

def get_val_pwntools(opcodes):
    # get code
    code = opcode_to_code(opcodes, b64=False)
    with open("stage3_samples/{}.S".format(context.arch), "w") as f:
        f.write(code)

    # run code in gdb
    gdb.debug_assembly(code)
    val = input("Value? ")
    return val

# Stage 3
def get_val(opcodes):
    # get code
    code = opcode_to_code(opcodes, b64=False)
    if not os.path.exists("stage3_samples/{}.S".format(context.arch)):
        with open("stage3_samples/{}.S".format(context.arch), "w") as f:
            f.write(code)
    # temporary
    return

    # generate asm file
    os.system("sed -e 's/AAAAAA/{0}/g' stage3/{1}.tmp.s > {1}.S".format(code, context.arch))

    # compile code
    if context.arch == "i386":
        os.system("as --32 -o i386.o i386.S")
        os.system("gcc -static -m32 -o code i386.o")
    elif context.arch == "amd64":
        os.system("nasm -f elf64 -o amd64.o amd64.S")
        os.system("ld -o code amd64.o")
    elif context.arch == "aarch64":
        os.system("aarch64-linux-gnu-as -o aarch64.o aarch64.S")
        os.system("aarch64-linux-gnu-gcc -static -o code aarch64.o")
    elif context.arch == "arm":
        os.system("arm-linux-gnueabihf-as -o arm.o arm.S")
        os.system("arm-linux-gnueabihf-gcc -static -o code arm.o")
    elif context.arch == "powerpc":
        os.system("powerpc-linux-gnu-as -o ppc32.o ppc32.S")
        os.system("powerpc-linux-gnu-gcc -o code ppc32.o")
    elif context.arch == "mips":
        log.failure("Got mips, F")
        sys.exit(1)
    else:
        log.failure("Invalid arch/mode")
        sys.exit(1)

    # get value
    a = process("./code")
    val = a.recvall(timeout=1)
    log.info("Answer is 0x" + hex(int(val)))
    return hex(int(val))

def stage1(p):
    log.info("Stage 1")
    code = get_asm(p)
    set_arch(code)

    # if context.arch == "mips":
    #     code = ".set noat\n" + code
    #     asm_code = asm(code)
    #     md = Cs(CS_ARH_MIPS, CS_MODE_MIPS32)

    encoded = b64encode(asm(code))
    p.sendline(encoded)

def stage2(p):
    log.info("Stage 2")
    b64_op = get_opcode(p)
    log.info("Data from remote: {}".format(b64_op))
    sol = b64encode(opcode_to_code(b64_op))
    if context.arch == "powerpc" or context.arch == "mips":
        log.info("Solution for stage 2: {}".format(sol))
    p.sendline(sol)

def stage3(p):
    log.info("Stage 3")
    input_raw = p.recvuntil("?", timeout=3).split(" is ")[1][:-1]
    log.info("Got {} opcodes from remote".format(len(input_raw)))
    input_hex_str = "\\x" + "\\x".join(x.encode("hex") for x in input_raw)
    log.info("cstr: {}".format(input_hex_str))
    p.sendline(("0x" if context.arch == "mips" else "") + hex(get_val_pwntools(input_raw)))

def main():
    p = init()

    for x in range(6):
        enter_room(p, x)
        #if x == 3:
        #    print p.recvall(timeout=3)
        stage1(p)
        stage2(p)
        stage3(p)

    enter_room(p, 6)
    print p.recvall(timeout=3)

if __name__ == "__main__":
    main()
