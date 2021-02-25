#!/usr/bin/env python
# coding: utf-8
#
# pkgdistcache daemon v0.3.1
# by Alessio Bianchi <venator85@gmail.com>
#

import http.server
import os
import os.path
import signal
import socket
import sys

import avahi
import dbus
import dbus.glib

avahi_service = None

colors = {'none': '\033[0m',
          'black': '\033[0;30m', 'bold_black': '\033[1;30m',
          'red': '\033[0;31m', 'bold_red': '\033[1;31m',
          'green': '\033[0;32m', 'bold_green': '\033[1;32m',
          'yellow': '\033[0;33m', 'bold_yellow': '\033[1;33m',
          'blue': '\033[0;34m', 'bold_blue': '\033[1;34m',
          'magenta': '\033[0;35m', 'bold_magenta': '\033[1;35m',
          'cyan': '\033[0;36m', 'bold_cyan': '\033[1;36m',
          'white': '\033[0;37m', 'bold_white': '\033[1;37m'}


def printmsg(msg):
    print("%s>> %s%s" % (colors['bold_blue'], msg, colors['none']))


def printerr(msg):
    print("%s!! %s%s" % (colors['bold_red'], msg, colors['none']))


def printwarn(msg):
    print("%s!! %s%s" % (colors['bold_yellow'], msg, colors['none']))


def terminate(signum, frame):
    avahi_service.unpublish()
    sys.exit(0)


class AvahiPublisher:
    # Based on http://avahi.org/wiki/PythonPublishExample
    def __init__(self, name, stype, host, port):
        self.name = name
        self.stype = stype
        self.domain = 'local'
        self.host = host
        self.port = port
        self.systemBus = dbus.SystemBus()
        self.server = dbus.Interface(
            self.systemBus.get_object(
                avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
            avahi.DBUS_INTERFACE_SERVER)

    def publish(self):
        self.group = dbus.Interface(
            self.systemBus.get_object(
                avahi.DBUS_NAME, self.server.EntryGroupNew()),
            avahi.DBUS_INTERFACE_ENTRY_GROUP)

        self.group.AddService(
            avahi.IF_UNSPEC,  # interface
            avahi.PROTO_UNSPEC,  # protocol
            dbus.UInt32(0),  # flags
            self.name, self.stype,
            self.domain, self.host,
            dbus.UInt16(self.port),
            avahi.string_array_to_txt_array([]))
        self.group.Commit()

    def unpublish(self):
        self.group.Reset()


class HTTPServerV6(http.server.HTTPServer):
    address_family = socket.AF_INET6


def main(args):
    # load configuration file
    conf_file = '/etc/pkgdistcache.conf'
    if os.path.isfile(conf_file):
        config = eval(open(conf_file).read())
    else:
        printerr("Config file " + conf_file + " not found")
        return 2

    port = config['port']
    hostname = socket.gethostname()
    global avahi_service
    avahi_service = AvahiPublisher(hostname, '_pkgdistcache._tcp', '', port)
    avahi_service.publish()

    chdir = config['chdir']
    os.chdir(chdir)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = HTTPServerV6(('', port), handler)

    try:
        # Disable useless polling since we never call shutdown
        httpd.serve_forever(poll_interval=None)
    except KeyboardInterrupt:
        avahi_service.unpublish()

    return 0


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, terminate)
    main(sys.argv)
