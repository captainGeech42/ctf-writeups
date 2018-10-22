#!/usr/bin/env python3

import json
import pprint
pprint._sort = lambda x: x
from collections import Counter

def is_printable(char):
    return char >= 0x21 and char <= 0x7e

def append(s, c): 
    c = int(c, 16)
    if is_printable(c):
        s += chr(c)
    return s

def get_uniq(l):
    u = []
    for i in l:
        if len(u) == 0 or u[len(u)-1] != i:
            u.append(i)
    return u

def get_char(color):
    if color == "Black":
        return "#"
    elif color == "White":
        return " "
    elif color == "Lightgray":
        return "*"
    elif color == "Birch":
        return "^"
    else:
        return "."

# read in json data
with open("ev3_data.json", "r") as f:
    data = json.load(f)

LOCALHOST="00:00:00:00:00:00"
EV3="00:16:53:61:30:c1"

TIMED_MOTOR="13:00:2a:00:00:00:00:af:00:06:0a:00:83:80:bb:00:00:82:e8:03:00"
READ_COLOR="0d:00:2a:00:00:04:00:99:1d:00:02:00:02:01:60"
READ_GYRO="0d:00:2a:00:00:04:00:99:1d:00:01:00:00:01:60"
SYNC_MOTOR_FLIP="0e:00:2a:00:00:00:00:b0:00:06:05:82:c8:00:00:01"
STEP_MOTOR="0e:00:2a:00:00:00:00:ae:00:06:0a:00:81:3c:1e:00"
SYNC_MOTOR_UNKNOWN="0e:00:2a:00:00:00:00:b0:00:06:05:82:38:ff:00:01"

to_ev3 = []
to_lh = []

cmds = []
cmd = ""
prev_cmd = ""

curr_coord = []
prev_coord = []
x = 0
y = 0
facing = "East"

color = ""

sensor_data = []

for packet in data:
    layers = packet["_source"]["layers"]
    
    if "bluetooth" in layers:
        src = layers["bluetooth"]["bluetooth.src"]
        dst = layers["bluetooth"]["bluetooth.dst"]

    if "data" in layers:
        raw_hex = layers["data"]["data.data"]
        data_len = int(layers["data"]["data.len"])

    if src and dst and raw_hex and data_len:
        if src == LOCALHOST:
            if raw_hex not in to_ev3:
                to_ev3.append(raw_hex)
            
            if raw_hex == TIMED_MOTOR:
                cmd = "Timed Motor"
            elif raw_hex == READ_COLOR:
                cmd = "Read Color Sensor"
            elif raw_hex == READ_GYRO:
                cmd = "Read Gyro Sensor"
            elif raw_hex == SYNC_MOTOR_FLIP:
                cmd = "Motors synced (flip)"
            elif raw_hex == STEP_MOTOR:
                cmd = "Motors stepped"
            elif raw_hex == SYNC_MOTOR_UNKNOWN:
                cmd = "Motors synced (unknown)"
            else:
                # there is a broken cmd, packets 2066 and 2072
                # the read color got broken into two packets
                cmd = "Read Color Sensor"

            if cmd == prev_cmd:
               cmds[len(cmds)-1]["count"] += 1
            else:
                # do state machine stuff
                if cmd == "Read Gyro Sensor" and prev_cmd == "Read Color Sensor":
                    # we are done reading, and now we rotate
                    y += 1
                    facing = "East" if facing == "West" else "West"

                cmds.append({"cmd": cmd, "count": 1})
                prev_cmd = cmd

        else: # EV3 --> localhost
            #if raw_hex not in to_lh:
            to_lh.append(raw_hex)

            if cmd == "Read Color Sensor":
                # 80:## is black, c0:## is white
                code = raw_hex.split("00:00:")[1]
                if code == "80:3f":
                    color = "Black"
                elif code == "c0:40":
                    color = "White"
                elif code == "40:40":
                    color = "Lightgray"
                elif code == "00:40":
                    color = "Birch"
                else:
                    color = "Gray"

                # increment/decrement x for each read 
                x += 1 if facing == "East" else -1

            elif cmd == "Read Gyro Sensor":
                d = raw_hex.split("02:00:")[1]
                x1 = int(d[0], 16)
                x2 = int(d[1], 16)

                if len(prev_coord) == 0:
                    prev_coord = [x1, x2]
                    continue

                prev_coord = [x1, x2]

            sensor_data.append({"color": color, "x": x, "y": y, "facing": facing})

uniq_data = get_uniq(sensor_data)

output = [""]*13

for i in range(len(uniq_data)):
    if i == 0:
        output[0] += get_char(uniq_data[i]["color"])
        continue
    
    if uniq_data[i]["x"] > uniq_data[i-1]["x"]:
        output[uniq_data[i]["y"]] += get_char(uniq_data[i]["color"])
    else:
        output[uniq_data[i]["y"]] = get_char(uniq_data[i]["color"]) + output[uniq_data[i]["y"]] 

for i in range(len(output)):
    print(i,output[i])