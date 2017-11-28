#! /usr/bin/python3
#
# (C) 2017 juergen@fabmail.org, distribute under GPLv2 or ask.
#
# Requires:
#  - apt-get install python3-pip
#  - apt-get install libffi-dev libssl-dev python3-dev
#  - pip3 install -U pip setuptools
#  - pip3 install python-miio
#  - git clone https://github.com/rytilahti/python-miio.git && ( cd python-miio; python3 setup.py install )
#
# 2017-11-22, jw	discover and timer.


import miio
import socket, codecs, time, sys, select
from miio.protocol import Message

def mirobo_discover():
        """
        Scan for devices in the network.
        Code taken from /usr/local/lib/python3.5/dist-packages/miio/device.py:def discover()
        """
        timeout = 5
        seen_addrs = []  # type: List[str]
        seen_tokens = []  # type: List[str]
        addr = '192.168.8.1'    # '<broadcast>'

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


if __name__ == '__main__':
        bots = mirobo_discover()
        if bots is None or len(bots) == 0:
        	js.close()
        	sys.exit("No robots found. Please check your wlan is connected to a robot\n")

        bot = miio.Vacuum(ip=bots[0][0], token=bots[0][1], start_id=0, debug=True)

        print("timezone=",bot.timezone())
        print(bot.timer())                     # id=1505168889826
        # bot.delete_timer(1505168889826)
        #
        # cron:
        # MIN HOUR DAY MON WDAY
        #   0    8   *   * 0,1,2,3,4,5,6
        #
        #                                             fan_speed
        # bot.add_timer('35 18 * * *', 'start_clean', 99)

