#! /usr/bin/python3
#
# http://python-evdev.readthedocs.io/en/latest/tutorial.html
# http://python-evdev.readthedocs.io/en/latest/apidoc.html
# cat /sys/devices/pci0000\:00/0000\:00\:14.0/usb2/2-3/2-3\:1.0/0003\:0E8F\:0003.0008/input/input24/name
#  MY-POWER CO.,LTD. USB Joystick
# cat /sys/devices/pci0000\:00/0000\:00\:14.0/usb2/2-3/2-3\:1.0/0003\:0E8F\:0003.0008/input/input24/capabilities/abs
#  10000030027
# cat /sys/devices/pci0000\:00/0000\:00\:14.0/usb2/2-3/2-3\:1.0/0003\:0E8F\:0003.0008/input/input24/modalias 
#  input:b0003v0E8Fp0003e0110-e0,1,3,4,15,k120,121,122,123,124,125,126,127,128,129,12A,12B,ra0,1,2,5,10,11,28,m4,lsf50,51,58,59,5A,60,w
#
# study fftest.c from https://git.code.sf.net/p/linuxconsole/code
# study python3 -m evdev.evtest
#
# Requires: 
#  - apt-get install pyhton3-pip
#  - pip3 install --upgrade pip
#  - pip3 install pip3 install setuptools
#  - pip3 install evdev
#
# (C) 2017 juergen@fabmail.org, distribute under GPLv2 or ask.
#

import evdev, select

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
        print("rattle", effnr, effgain)
        gain = evdev.InputEvent(0, 0, evdev.ecodes.EV_FF, evdev.ecodes.FF_GAIN, effgain)    # [0x5000 .. 0xFFFF]
        play = evdev.InputEvent(0,0,evdev.ecodes.EV_FF, effnr, 1)
        stop = evdev.InputEvent(0,0,evdev.ecodes.EV_FF, effnr, 0)
        d.write_event(gain)
        d.write_event(play)

devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]

device_fn=None
for device in devices:
        print(device.fn, device.name, device.phys)
        device_fn=device.fn

device = evdev.InputDevice(device_fn)
init_rattle(device)

def js_read_loop(dev, timeout):
        """
        same as /usr/local/lib/python3.5/dist-packages/evdev/eventio.py:read_loop, but with a timeout...
        """
        while True:
                r, w, x = select.select([dev.fd], [], [], timeout)
                if len(r):
                        for event in dev.read():
                                yield event
                else:
                        yield evdev.InputEvent(0,0,evdev.ecodes.EV_SYN, evdev.ecodes.KEY_UNKNOWN,0)     # dummy when timout


for ev in js_read_loop(device, 3.0):
        if ev.type == evdev.ecodes.EV_KEY:
                print("key", ev.value, ev.code, decode_ecode(ev.code))
                if   ev.code == evdev.ecodes.BTN_TRIGGER and ev.value == 1: rattle(device, 0)  # 288
                elif ev.code == evdev.ecodes.BTN_THUMB   and ev.value == 1: rattle(device, 1)  # 289
                elif ev.code == evdev.ecodes.BTN_THUMB2  and ev.value == 1: rattle(device, 2)  # 290
                elif ev.code == evdev.ecodes.BTN_TOP     and ev.value == 1: rattle(device, 3)  # 291
        elif ev.type == evdev.ecodes.EV_ABS:
                print("abs", ev.value, ev.code, decode_ecode(ev.code))
        elif ev.type == evdev.ecodes.EV_FF:
                if ev.code < 16:                # 96 is gain setting.
                        if ev.value:
                                print("ff %d start" % ev.code)
                        else:
                                print("ff %d stop" % ev.code)
        elif ev.type in (evdev.ecodes.EV_SYN, evdev.ecodes.EV_MSC):
                pass
        else:
                print(ev.type, ev.value, ev.code, repr(evdev.categorize(ev)))


