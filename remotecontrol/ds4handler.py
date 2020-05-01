# lightly adapted from CSG Show S1:E2, available at:
# https://github.com/codingwithsomeguy/codingwithsomeguy/blob/master/theshow/s1/e2/keyhandler.py

import os
import json
import struct
import re

# xinput list
XINPUT_KB_NAME = "Sony Computer Entertainment Wireless Controller Touchpad"
INPUT_EVENT_NAME = "/dev/input/by-id/usb-Sony_Computer_Entertainment_Wireless_Controller-event-joystick"
INPUT_EVENT_FORMAT = "@lIIHHi"
INPUT_EVENT_SIZE = struct.calcsize(INPUT_EVENT_FORMAT)
SCANCODE_FILE = "scancodes-to-keynames.json"
ABS_MAPPING = "evcode-to-absnames.json"


def disable_xinput():
    DOWN_ARROW = "\u21b3"
    for line in os.popen("xinput list").readlines():
        if line.find(XINPUT_KB_NAME) != -1:
            xi_kb_name = line.split(DOWN_ARROW)[1].split("\t")[0][1:].strip()
            cmd = "xinput disable \"%s\"" % xi_kb_name
            #print(cmd)
            os.system(cmd)


def process_key(key_name):
    print(key_name)
    commands = {
        "KEY_Q": "echo 'I do nothing fun' &",
        "KEY_X": "xeyes &",
        "KEY_C": "chromium --incognito 'https://duckduckgo.com/?q=RFC+HTCPCP' &",
    }
    if key_name in commands:
        #print(commands[key_name])
        os.system(commands[key_name])


def send_key(key_name):
    # based on /usr/include/X11/keysymdef.h
    key_to_xkeysym = {
        "DS4_BUTTON_LEFT": "Left", "DS4_BUTTON_RIGHT": "Right",
        "DS4_BUTTON_UP": "Up", "DS4_BUTTON_DOWN": "Down",
        "DS4_BUTTON_CROSS": "B", "DS4_BUTTON_CIRCLE": "A",
        "DS4_BUTTON_TRIANGLE": "X", "DS4_BUTTON_SQUARE": "Y",
    }

    if key_name in key_to_xkeysym:
        cmd = "/usr/bin/xdotool key '%s'" % key_to_xkeysym[key_name]
        os.system(cmd)
    else:
        print("unmapped key: " + key_name)
    

def decode_event(raw_event):
    scancode_decoder = json.load(open(SCANCODE_FILE))
    abs_mapping_decoder = json.load(open(ABS_MAPPING))

    et = struct.unpack(INPUT_EVENT_FORMAT, raw_event)
    (et_tv_sec, et_tv_usec, _, ev_type, ev_code, ev_value) = et
    EV_SYN = 0x00
    EV_KEY = 0x01
    EV_REL = 0x02
    EV_ABS = 0x03
    KEYDOWN = 0x01

    ds4_buttons = {
        "304": "DS4_BUTTON_CROSS",
        "305": "DS4_BUTTON_CIRCLE",
        "307": "DS4_BUTTON_TRIANGLE",
        "308": "DS4_BUTTON_SQUARE",
        "310": "DS4_BUTTON_L1",
        "311": "DS4_BUTTON_R1",
        "312": "DS4_BUTTON_L2",
        "313": "DS4_BUTTON_R2",
        "314": "DS4_BUTTON_SHARE",
        "315": "DS4_BUTTON_OPTIONS",
        "316": "DS4_BUTTON_PSN",
        "317": "DS4_BUTTON_L3",
        "318": "DS4_BUTTON_R3",
    }
    
    if ev_type == EV_KEY and ev_value == KEYDOWN:
        #print(ev_type, ev_code, ev_value)
        ev_code_str = str(ev_code)
        #if ev_code_str in scancode_decoder:
            #process_key(scancode_decoder[ev_code_str])
        if ev_code_str in ds4_buttons:
            send_key(ds4_buttons[ev_code_str])
    elif ev_type == EV_ABS:
        abs_code = abs_mapping_decoder[str(ev_code)]
        if abs_code not in ["ABS_RX", "ABS_RY", "ABS_Y", "ABS_X", "ABS_Z", "ABS_RZ"]:
            #print(ev_type, ev_code, ev_value)
            if abs_code == "ABS_HAT0X":
                #print("X axis")
                if ev_value == -1:
                    send_key("DS4_BUTTON_LEFT")
                elif ev_value == 1:
                    send_key("DS4_BUTTON_RIGHT")
                elif ev_value == 0:
                    #print("center")
                    pass
            elif abs_code == "ABS_HAT0Y":
                #print("Y axis")
                if ev_value == -1:
                    send_key("DS4_BUTTON_UP")
                elif ev_value == 1:
                    send_key("DS4_BUTTON_DOWN")
                elif ev_value == 0:
                    #print("center")
                    pass


def main():
    #disable_xinput()
    with open(INPUT_EVENT_NAME, "rb") as f:
        while True:
            raw_event = f.read(INPUT_EVENT_SIZE)
            decode_event(raw_event)


if __name__ == "__main__":
    main()
