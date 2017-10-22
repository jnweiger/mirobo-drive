#! /usr/bin/python
#
# http://python-evdev.readthedocs.io/en/latest/tutorial.html
# http://python-evdev.readthedocs.io/en/latest/apidoc.html
# cat /sys/devices/pci0000\:00/0000\:00\:14.0/usb2/2-3/2-3\:1.0/0003\:0E8F\:0003.0008/input/input24/name
#  MY-POWER CO.,LTD. USB Joystick
# cat /sys/devices/pci0000\:00/0000\:00\:14.0/usb2/2-3/2-3\:1.0/0003\:0E8F\:0003.0008/input/input24/capabilities/abs
#  10000030027
# cat /sys/devices/pci0000\:00/0000\:00\:14.0/usb2/2-3/2-3\:1.0/0003\:0E8F\:0003.0008/input/input24/modalias 
#  input:b0003v0E8Fp0003e0110-e0,1,3,4,15,k120,121,122,123,124,125,126,127,128,129,12A,12B,ra0,1,2,5,10,11,28,m4,lsf50,51,58,59,5A,60,w


import evdev, sys, time
# from evdev import InputDevice

if len(sys.argv) < 2:
  print("Usage: %s /dev/input/event16" % sys.argv[0])
  sys.exit(0)

# '/dev/input/event16')
dev = evdev.InputDevice(sys.argv[1])

print(dev.leds(verbose=True), evdev.ecodes.LED_NUML, evdev.ecodes.LED_CAPSL)

while (True):
  for i in range(256): dev.set_led(i, 1)
  time.sleep(0.1)
  for i in range(256): dev.set_led(i, 0)
  time.sleep(0.1)
  print('.',)


for event in dev.read_loop():
  print(event)
