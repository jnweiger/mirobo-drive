# mirobo-drive
Control a Xiaomi Mi robot with a USB gamepad controller

# Get the token
<pre># study https://github.com/rytilahti/python-miio
sudo apt-get install libffi-dev libssl-dev
sudo apt-get install python3-dev        # Python.h neede for miio dependency cffi
sudo pip3 install -U pip setuptools
sudo pip3 install python-miio
 -> this brings a long list of dependencies... always do that, even if you want to use the git checkout.

mirobo discover --handshake 1
 INFO:mirobo.device:Sending discovery to <broadcast> with timeout of 5s..
 INFO:mirobo.device:  IP 192.168.8.1: 986 - token: b'xxxxxxxxxxxxxxxxxxxxxxxxxx'

export MIROBO_IP=192.168.8.1 MIROBO_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
mirobo find
 Sending find the robot calls.
 0
 "Hi, I'm over here!"

mirobo start
 "Strting the cleanup"
mirobo home
 "Going back to the dock" --> "charging"
</pre>

# sniff the traffic
<pre># the vacuum cleaner is set to connect to WLAN $guest with well known password.
# We create the $guest network with a TP-Link router having its default gateway
# on a lan port connected to a linux laptop.
# The linux laptop is connected with wlan to the internet and acts as a NAT router
# between its LAN and WLAN.

# Reset the tplink router by holding the reset button for 5 seconds
# connect laptop to a lan cable.
 -> laptop gets 192.168.1.144 per dhcp from the tplink.
firefox http://192.168.1.1
 -> user: admin
 -> pass: admin
  -> set a root password, enable ssh
  -> add ssh key on the web gui (ssh-copy-id does not work into openwrt)
 -> Network -> Wifi -> General Setup
   ESSID: [$guest]
   Mode: Access Point
   Network: [x] LAN
 -> Network -> Wifi -> Wireless Security
  WPA-PSK/WPA-PSK2 Mixed mode
  Key: [.....]

 -> DHCP and DNS
 DNS forwarding [8.8.8.8]
 rockrobo               192.168.1.156   34:ce:00:ea:12:dc       9h 47m 13s
 jw-ThinkPad-X200s      192.168.1.144   00:1f:16:2b:da:60       11h 21m 18s

landev=enp0s25
ip route del default via 192.168.1.1
ip route add  192.168.1.0/24 dev enp0s25        # if missing.
#-> connect laptop to internet via wlan
dmesg | grep ': associated' | tail -1
 [56262.881537] wls1: associated
extdev=wls1
iptables -t nat -A POSTROUTING -o $extdev -j MASQUERADE
iptables -A FORWARD -i $extdev -o $landev -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $landev -o $extdev -j ACCEPT

ssh -v root@192.168.1.1
route add default via 192.168.1.144
ping 8.8.8.8
 -> should work now.
exit # back to the linux laptop
</pre>

# Resources

https://www.thingiverse.com/thing:2615052

http://python-evdev.readthedocs.io/en/latest/

https://github.com/marcelrv/XiaomiRobotVacuumProtocol

https://github.com/rytilahti/python-miio

https://github.com/aholstenson/miio/

https://github.com/jghaanstra/com.xiaomi-miio

https://github.com/jghaanstra/com.robot.xiaomi-mi

https://github.com/stianaske/pybotvac

https://apps.athom.com/app/com.xiaomi-miio

https://community.openhab.org/t/xiaomi-mi-robot

