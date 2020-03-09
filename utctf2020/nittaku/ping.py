from scapy.all import *
import sys
import string

f = ""

id = 0x1337
for x in range(0x10000,0x1000, -1):
    packet = Ether()/IP(dst="3.88.183.122",ttl=64,id=0x1234)/ICMP(type=8,code=0,id=id,seq=x)/("\x00"*48)
    ans, unans= srp(packet)

    data = ans[0][1][Raw].load.strip()

    if data[0] not in string.printable:
        break

    print("Packet {}: {}".format(x,len(data)))
    f += data

    print(repr(data))
    # assert(len(data) == 1024)


with open("dump_{}.b64".format(hex(id)[2:]), "w") as fi:
    fi.write(f.rstrip("\x00").strip())
