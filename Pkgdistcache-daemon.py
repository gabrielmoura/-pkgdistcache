#!/usr/bin/env python
# coding: utf-8
#
# pkgdistcache daemon v0.3.1
# by Alessio Bianchi <venator85@gmail.com>
#
# Daemon code by Chad J. Schroeder
# http://code.activestate.com/recipes/278731/
#

import sys
import os
import os.path
import subprocess
import string
import avahi
import dbus
from gi.repository import GObject as gobject
import dbus.glib
import http.server
import signal
import socket

avahi_service = None


def terminate(signum, frame):
    avahi_service.unpublish()
    sys.exit(0)


# Run a command synchronously, redirecting stdout and stderr to strings
def runcmd(cmd, cwd=None):
    pipe = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = pipe.communicate()  # wait for process to terminate and return stdout and stderr
    return {'stdout': stdout.strip(), 'stderr': stderr.strip(), 'retcode': pipe.returncode}


# Detach a process from the controlling terminal and run it in the background as a daemon
def daemonize():
    try:
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if (pid == 0):  # The first child.
        os.setsid()
        try:
            pid = os.fork()  # Fork a second child.
        except OSError as e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))

        if (pid != 0):  # The second child.
            os._exit(0)  # Exit parent (the first child) of the second child.
    else:
        os._exit(0)  # Exit parent of the first child.

    import resource  # Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = 1024

    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:  # ERROR, fd wasn't open to begin with (ignored)
            pass

    # The standard I/O file descriptors are redirected to /dev/null by default.
    os.open("/dev/null", os.O_RDWR)  # standard input (0)
    os.dup2(0, 1)  # standard output (1)
    os.dup2(0, 2)  # standard error (2)
    return (0)


class AvahiPublisher:
    # Based on http://avahi.org/wiki/PythonPublishExample
    def __init__(self, name, stype, host, port):
        self.name = name
        self.stype = stype
        self.domain = 'local'
        self.host = host
        self.port = port
        self.systemBus = dbus.SystemBus()
        self.server = dbus.Interface(self.systemBus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
                                     avahi.DBUS_INTERFACE_SERVER)

    def publish(self):
        self.group = dbus.Interface(
            self.systemBus.get_object(avahi.DBUS_NAME, self.server.EntryGroupNew()),
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
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-F", "--foreground", action="store_true", dest="no_daemon", default=False,
                      help="run pkgdistcache-daemon in foreground")
    (options, args) = parser.parse_args()
    if options.no_daemon == False:
        # fork daemon in background
        daemonize()

    # load configuration file
    conf_file = '/etc/pkgdistcache.conf'
    if os.path.isfile(conf_file):
        config = eval(open(conf_file).read())
    else:
        printerr("Config file " + conf_file + " not found")
        return 2

    port = config['port']
    hostname = runcmd('hostname')['stdout']
    global avahi_service
    avahi_service = AvahiPublisher(hostname, '_pkgdistcache._tcp', '', port)
    avahi_service.publish()

    os.chdir('/var/cache/pacman/pkg')
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
