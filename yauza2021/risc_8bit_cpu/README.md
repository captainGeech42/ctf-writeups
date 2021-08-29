# RISC 8bit CPU

> The SFT0 CPU is a secure processor designed to store encryption key. Find out how the processor works and get the key.

I made a (jank) Binary Ninja architecture plugin and an emulator that solves this challenge.

## Note

The challenge author said on Discord that the binary provided has a bug, the conditional jumps must have 4 bytes added to the destination addresses. That change is reflected in the emulator (along with a disclaimer comment).
