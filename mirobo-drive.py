#! /usr/bin/python3
#
# (C) 2017 juergen@fabmail.org, distribute under GPLv2 or ask.
#
# http://python-evdev.readthedocs.io/en/latest/apidoc.html
#
# study fftest.c from https://git.code.sf.net/p/linuxconsole/code
# study python3 -m evdev.evtest
#
# Requires: 
#  - apt-get install pyhton3-pip
#  - pip3 install pip3 install -U pip setuptools
#  - pip3 install evdev
#
#  - apt-get install libffi-dev libssl-dev python3-dev
#  - pip3 install -U pip setuptools
#  - pip3 install python-miio


import miio
import socket, codecs, time, sys
from miio.protocol import Message

import evdev

def mirobo_discover():
        """
        Scan for devices in the network.
        Code taken from /usr/local/lib/python3.5/dist-packages/miio/device.py:def discover()
        """
        timeout = 5
        seen_addrs = []  # type: List[str]
        seen_tokens = []  # type: List[str]
        addr = '<broadcast>'

        # magic, length 32
        helobytes = bytes.fromhex(
            '21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        for _i in range(3):
            s.sendto(helobytes, (addr, 54321))
        while True:
            try:
                data, addr = s.recvfrom(1024)
                m = Message.parse(data)  # type: Message
                # print("Got a response: %s" % m)

                if addr[0] not in seen_addrs:
                    token = codecs.encode(m.checksum, 'hex')
                    if type(token) is bytes: token = token.decode()     # tostring
                    print("  IP %s: %s - token: %s" % (
                        addr[0],
                        m.header.value.devtype,
                        token))
                    seen_addrs.append(addr[0])
                    seen_tokens.append([addr[0], token])
            except socket.timeout:
                print("Discovery done")
                return seen_tokens
            except Exception as ex:
                print("error while reading discover results: %s", ex)
                break
        return None
 


def decode_ecode(n):
        names = []
        for i in reversed(sorted(evdev.ecodes.ecodes)):           # BTN_JOYSTICK and BTN_TRIGGER are bot 288
                if evdev.ecodes.ecodes[i] == n:
                        names.append(i)
        return names

def init_rattle(d):
        """
ioctl(3, EVIOCSFF, {type=FF_PERIODIC, id=4294967295, direction=16384, trigger={button=0, interval=0}, replay={lenght=20000, delay=1000}, periodic_ef={waveform=90, period=10, magnitude=32767, offset=0, phase=0, envelope={attack_length=1000, attack_level=32767, fade_length=1000, fade_level=7fff}, custom_len=0, *custom_data=0}) = 0
Uploading effect #0 (Periodic sinusoidal) ... ", 46) = 46
"Q\0\377\377\0@\0\0\0\0 N\350\3\0\0Z\0\n\0\377\177\0\0\0\0\350\3\377\177\350\3\377\177\0\0\0\0\0\0\0\0\0\0\0\0\0\0", 48) = 48


ioctl(3, EVIOCSFF, {type=FF_RUMBLE, id=4294967295, direction=12079, trigger={button=12079, interval=12079}, replay={lenght=5000, delay=1000}, rumble={strong_magnitude=32768, weak_magnitude=0}) = 0

ioctl(3, EVIOCSFF, {type=FF_RUMBLE, id=4294967295, direction=0, trigger={button=0, interval=0}, replay={lenght=5000, delay=0}, rumble={strong_magnitude=0, weak_magnitude=49152}) = 0

        """
        for e in range(6):
            try: d.erase_effect(e)
            except: pass
        def upload_effect(dev, buf):
            return evdev._input.upload_effect(dev.fd, buf)

        # length=\xf4\x01        500
        # length=\xe8\x03       1000
        # length=\xd0\x07       2000
        # length=\xa0\x0f       4000
        #                PERI id         but int length dela
        upload_effect(d, b'Q\0\377\377\0@\0\0\0\0\xf4\x01\0\0\0\0Z\0\n\0\377\177\0\0\0\0\350\3\377\177\350\3\377\177\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
        upload_effect(d, b'Q\0\377\377\0@\0\0\0\0\xe8\x03\0\0\0\0Z\0\n\0\377\177\0\0\0\0\350\3\377\177\350\3\377\177\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
        upload_effect(d, b'Q\0\377\377\0@\0\0\0\0\xd0\x07\0\0\0\0Z\0\n\0\377\177\0\0\0\0\350\3\377\177\350\3\377\177\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
        upload_effect(d, b'Q\0\377\377\0@\0\0\0\0\xa0\x0f\0\0\0\0Z\0\n\0\377\177\0\0\0\0\350\3\377\177\350\3\377\177\0\0\0\0\0\0\0\0\0\0\0\0\0\0')

def rattle(d, effnr=0, effgain=0xC000):
        print("rattle", effnr, hex(effgain))
        gain = evdev.InputEvent(0, 0, evdev.ecodes.EV_FF, evdev.ecodes.FF_GAIN, effgain)    # [0x5000 .. 0xFFFF]
        play = evdev.InputEvent(0,0,evdev.ecodes.EV_FF, effnr, 1)
        stop = evdev.InputEvent(0,0,evdev.ecodes.EV_FF, effnr, 0)
        d.write_event(gain)
        d.write_event(play)

def init_joystick():
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]

        device_fn=None
        for device in devices:
                print(device.fn, device.name, device.phys)
                # take the last one.
                device_fn=device.fn

        device = evdev.InputDevice(device_fn)
        init_rattle(device)
        return device


js = init_joystick()

rattle(js, 2, 0x5000)
bots = mirobo_discover()
for bot in bots:
	rattle(js, 0, 0xf000)
	time.sleep(1.0)
rattle(js, 2, 0x5000)
time.sleep(2.5)

if bots is None or len(bots) == 0:
	js.close()
	sys.exit("No robots found. Please check your wlan is connected to a robot\n")

bot = miio.Vacuum(ip=bots[0][0], token=bots[0][1], start_id=0, debug=True)

# /usr/local/lib/python3.5/dist-packages/miio/vacuum.py
# /usr/local/lib/python3.5/dist-packages/miio/vacuum_cli.py

# button assignments on my el-cheapo ps3 controller:
#
# left lower front:     L2      BTN_BASE        stop.
# left upper front:     L1      BTN_TOP2        start manual mode.
# right lower front:    R2      BTN_BASE2       (switch to manual &) move forward
# right upper front:    R1      BTN_PINKIE      (switch to manual &) turn 60 deg ccw.
#
# right cross north:    1       BTN_TRIGGER     find
# right cross east:     2       BTN_THUMB       start cleaning
# right cross south:    3       BTN_THUMB2      dock
# right cross west:     4       BTN_TOP         spot cleaning
#
# left cross north:             ABS_HAT0Y, -1   increment volume 10%
# left cross south:             ABS_HAT0Y, 1    decrement volume 10%
# left cross east:              ABS_HAT0X, 1           
# left cross west:              ABS_HAT0X, -1           
#
# center left:          select  BTN_BASE3
# center right:         start   BTN_BASE4       toggle start/stop manual mode
#
# right joystick north:         ABS_RZ 127..0   
# right joystick south:         ABS_RZ 129..255
# right joystick east:          ABS_Z  129..255
# right joystick west:          ABS_Z  127..0
# right joystick down:          BTN_BASE6
#
# left joystick north:          ABS_Y  127..0
# left joystick south:          ABS_Y  129..255
# left joystick east:           ABS_X  129..255
# left joystick west:           ABS_X  127..0
# left joystick down:           BTN_BASE5

botstate='Manual mode'
bot.manual_start()
# reported states are
#
#  Idle
#  Spot cleaning
#  Cleaning
#  Charging
#
#  Returning home
#  Charger disconnected

fan_speed = [ 1, 30, 50, 70, 80, 100 ]
fan_speed_idx = 0
def bot_fan():
        print("fanspeed set", fan_speed[fan_speed_idx])
        bot.set_fan_speed(fan_speed[fan_speed_idx])

bot_fwd=128 # values last seen from the joystick ABS_RZ or ABS_Y axis, 128 is center, 0 is north, 255 is south.
bot_rot=128 # values last seen from the joystick ABS_Z  or ABS_X axis, 128 is center, 0 is west, 255 is east.

def bot_drive():
        if botstate != 'Manual mode':
                rattle(js, 1)
                return
        velocity = 0            # ]-0.3 .. 0.3[ bratwurst
        rotation = 0            # ]-180 .. 180[ degree
        duration = 1500         # msec
        if bot_fwd < 128:       # forwards full speed.
                velocity = (128-bot_fwd)/128.*0.299
        if bot_fwd > 128:       # backwards 1/2 rd speed.
                velocity = (128-bot_fwd)/128.*0.15
        rotation = (128-bot_rot)/128.0*100      # fastest 179
        print("bot_drive", rotation, velocity, duration)
        bot.manual_control(rotation, velocity, duration)

for ev in js.read_loop():
        if   ev.type == evdev.ecodes.EV_ABS:
                print("abs", ev.value, ev.code, decode_ecode(ev.code))
                if   ev.code in (evdev.ecodes.ABS_RZ, evdev.ecodes.ABS_Y):
                        bot_fwd = ev.value
                        bot_drive()
                elif ev.code in (evdev.ecodes.ABS_Z, evdev.ecodes.ABS_X):
                        bot_rot = ev.value
                        bot_drive()
                elif ev.code == evdev.ecodes.ABS_HAT0Y:
                        if ev.value < 0 and fan_speed_idx < len(fan_speed)-1: 
                                fan_speed_idx += 1
                                bot_fan()
                        if ev.value > 0 and fan_speed_idx > 0: 
                                fan_speed_idx -= 1
                                bot_fan()

        elif ev.type == evdev.ecodes.EV_KEY and ev.value == 1:
                if   ev.code == evdev.ecodes.BTN_TRIGGER:       # right cross North
                        bot.find()
                        res = bot.status()
                        print(botstate, res)
                        # transitions normally not seen:
                        #  Returning home -> Charging
                        botstate = res.state                    
                elif ev.code == evdev.ecodes.BTN_THUMB:         # right cross East
                        if botstate == 'Manual mode': bot.manual_stop()
                        botstate = 'Cleaning'
                        bot.start()
                elif ev.code == evdev.ecodes.BTN_THUMB2:        # right cross South
                        if botstate == 'Manual mode': bot.manual_stop()
                        botstate = 'Returning home'
                        bot.home()
                elif ev.code == evdev.ecodes.BTN_TOP:           # right cross West
                        if botstate == 'Manual mode': bot.manual_stop()
                        if botstate == 'Cleaning':   bot.stop()
                        botstate = 'Spot cleaning'
                        bot.spot()
                elif ev.code == evdev.ecodes.BTN_BASE4:          # center right:         start
                        if botstate == 'Manual mode':
                                bot.manual_stop()
                                botstate = 'Idle'
                        elif botstate == 'Idle':
                                bot.manual_start()
                                botstate = 'Manual mode'
                        elif botstate == 'Cleaning':
                                bot.stop()
                                botstate = 'Idle'
                        else:
                                print("Unknown state", botstate, "doing nothing.")
                        res = bot.status()
                        print(botstate, res)
                elif ev.code == evdev.ecodes.BTN_BASE:           # left front bottom
                        if botstate == 'Manual mode':
                                bot.manual_stop()
                        elif botstate == 'Cleaning':
                                bot.stop()
                        else:
                                print("Unknown state:", botstate, " -- doing nothing.")
                        botstate = 'Idle'
                        res = bot.status()
                        print(botstate, res)
                elif ev.code == evdev.ecodes.BTN_TOP2:           # left front bottom
                        bot.manual_start()
                        botstate = 'Manual mode'
