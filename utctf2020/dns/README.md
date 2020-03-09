Googling some strings leads to https://github.com/mwarning/SimpleDNS

`decode_domain_name` has a buffer overflow vuln

Shellcode in the name, pointer to rax at `decode_domain_name` return, there is also a `jmp rax` gadget, so we just jump to shellcode.

Unfortunately, you're communicating over UDP, so you have to something more creative to get the flag. I tried to do a TCP reverse shell but it didn't work remotely, so I switched to doing ORW via TCP for the flag file, which worked.

Shellcode is based on [this code](https://github.com/zerosum0x0/SLAE64/blob/master/reverseshell/reverseshell.asm)
