#!/usr/bin/env python
# coding: utf-8
#
# pkgdistcache client v0.3.1
# by Alessio Bianchi <venator85@gmail.com>
#

import collections
import os
import os.path
import pickle
import socket
import string
import subprocess
import sys

import avahi
import dbus
import dbus.glib
import requests
import xdg.BaseDirectory
from gi.repository import GLib

colors = {
    'none': '\033[0m',
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


# Run a command synchronously, sending stdout and stderr to shell
def runcmd2(cmd, cwd=None):
    pipe = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=None, stderr=None)
    pipe.communicate()  # wait for process to terminate
    return pipe.returncode


class Service(object):
    def __init__(self, service, host, ip, port):
        self.service = service
        self.host = host
        self.ip = ip
        self.port = port

    def __str__(self):
        return ("(%s, %s, %s, %d)"
                % (self.service, self.host, self.ip, self.port))

    def __repr__(self):
        # il tostring sulle liste è repr
        return self.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        return hash(self) == hash(other)


def once(func):
    def wrapped(*args):
        if wrapped.ran:
            return
        wrapped.ran = True
        return func(*args)

    wrapped.ran = False
    return wrapped


AvahiService = collections.namedtuple(
    'AvahiService',
    ['interface', 'protocol', 'name', 'stype', 'domain', 'flags'])
AvahiResolvedService = collections.namedtuple(
    'AvahiResolvedService',
    ['interface', 'protocol', 'name', 'type', 'domain', 'host',
     'aprotocol', 'address', 'port', 'txt', 'flags'])


class AvahiBrowser(object):
    def __init__(self):
        # Connect to the system bus...
        self.bus = dbus.SystemBus()
        # Get a proxy to the object we want to talk to.
        avahi_proxy = self.bus.get_object(
            avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER)
        # Set the interface we want to use; server in this case.
        self.server = dbus.Interface(avahi_proxy, avahi.DBUS_INTERFACE_SERVER)
        self.version_string = self.server.GetVersionString()
        self.domain = "local"
        self.services = {}

    def browse(self, stype, all_for_now_callback):
        all_for_now_callback = once(all_for_now_callback)

        # Ask the server for a path to the browser object for the service we're
        # interested in...
        browser_path = self.server.ServiceBrowserNew(
            avahi.IF_UNSPEC,
            avahi.PROTO_UNSPEC,
            stype,
            self.domain,
            dbus.UInt32(0))
        # Get it's proxy object...
        browser_proxy = self.bus.get_object(avahi.DBUS_NAME, browser_path)
        # And set the interface we want to use
        browser = dbus.Interface(
            browser_proxy, avahi.DBUS_INTERFACE_SERVICE_BROWSER)

        # Now connect the call backs to the relevant signals.
        browser.connect_to_signal('ItemNew', self._item_new)
        browser.connect_to_signal('ItemRemove', self._item_remove)
        browser.connect_to_signal('AllForNow', all_for_now_callback)

        def failure(*args):
            self._failure(*args)
            all_for_now_callback()

        browser.connect_to_signal('Failure', failure)

    def _item_new(self, *args):
        service = AvahiService(*args)
        if service.flags & avahi.LOOKUP_RESULT_LOCAL:
            # The service is on this machine; ignore
            return
        try:
            s = self.server.ResolveService(
                service.interface,
                service.protocol,
                service.name,
                service.stype,
                service.domain,
                avahi.PROTO_UNSPEC,
                dbus.UInt32(0))
            self.services[service] = AvahiResolvedService(*s)
        except dbus.DBusException as ex:
            # Mainly expect to see:
            # org.freedesktop.Avahi.TimeoutError: Timeout reached
            printwarn(ex)

    def _item_remove(self, *args):
        # The key will be missing if ResolveService raised an exception
        self.services.pop(AvahiService(*args), None)

    def _failure(self, error):
        printwarn(error)

    def discovered_services(self):
        return self.services.values()


def cache_main(argv):
    os.setsid()
    os.chdir('/')

    loop = GLib.MainLoop()

    GLib.timeout_add_seconds(60, loop.quit)

    lis = socket.fromfd(0, socket.AF_UNIX, socket.SOCK_STREAM)

    def start_accepting():
        channel = GLib.IOChannel.unix_new(lis.fileno())
        GLib.io_add_watch(channel, GLib.IO_IN, accept, None)

    def accept(source, condition, data):
        # TODO: reset quit timer?
        (sock, addr) = lis.accept()
        with sock:
            sock.shutdown(socket.SHUT_RD)
            # remove duplicates (eg services offered on more than a network
            # card etc.)
            clients = set()
            for client in browser.discovered_services():
                clients.add(Service(str(client.name), str(client.host),
                                    str(client.address), int(client.port)))
            pkgdistcache_clients = list(clients)
            with sock.makefile('wb') as f:
                pickle.dump(pkgdistcache_clients, f, -1)
        return True

    # discover other pkgdistcache capable hosts via avahi
    browser = AvahiBrowser()
    browser.browse("_pkgdistcache._tcp", start_accepting)

    loop.run()

    # We don't unlink the socket file, since we don't easily know whether our
    # current fd corresponds to the current file
    lis.close()
    return 0


def spawn_cache_process(cache_file):
    try:
        # Clean up stale file
        os.unlink(cache_file)
    except FileNotFoundError:
        pass
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(cache_file)
        except OSError as e:
            if e.errno != 98:
                raise
            # OSError: [Errno 98] Address already in use
            return  # Assume race, where a cache process is already running

        sock.listen()
        subprocess.Popen([__file__, '--cache'], stdin=sock)


def connect_to_cache_process(cache_file):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    while True:
        try:
            sock.connect(cache_file)
            return sock
        except (FileNotFoundError, ConnectionRefusedError):
            spawn_cache_process(cache_file)


def fetch_from_peer(pkg, dst, download_cmd_template):
    runtime_dir = xdg.BaseDirectory.get_runtime_dir(strict=False)
    cache_file = os.path.join(runtime_dir, 'pkgdistcache')

    with connect_to_cache_process(cache_file) as sock:
        sock.shutdown(socket.SHUT_WR)
        with sock.makefile('rb') as f:
            pkgdistcache_clients = pickle.load(f)

    if pkgdistcache_clients:
        print("-- Discovered hosts: %s"
              % ", ".join(set([c.host for c in pkgdistcache_clients])))
    else:
        print("-- No hosts discovered")

    for client in pkgdistcache_clients:
        clientip = client.ip
        if ":" in clientip:
            clientip = "[" + clientip + "]"
        url = "http://" + clientip + ":" + str(client.port) + "/" + pkg
        try:
            r = requests.head(url, timeout=1)
        except Exception as e:
            printwarn("Failed checking host '%s' with ip '%s': %s"
                      % (client.host, clientip, repr(e)))
            continue
        if r.status_code != 200:
            continue

        printmsg("Downloading %s from host '%s'" % (pkg, client.host))
        download_cmd = download_cmd_template.substitute(
            {'u': url, 'o': dst})
        ret = runcmd2(download_cmd)
        if ret == 0:
            return True
        else:
            printwarn("Host '%s' doesn't have %s in cache"
                      % (client.host, pkg))
    return False


def main(argv):
    # load configuration file
    conf_file = '/etc/pkgdistcache.conf'
    if os.path.isfile(conf_file):
        config = eval(open(conf_file).read())
    else:
        printerr("Config file " + conf_file + " not found")
        return 2

    download_cmd_template = string.Template(config['download_cmd'])

    pkg = os.path.basename(argv[1])  # argv[1] = %u passed by pacman
    dst = argv[2]  # argv[2] = %o passed by pacman

    must_download = True
    if not (pkg.endswith('.db') or pkg.endswith('.db.sig')):
        try:
            must_download = not fetch_from_peer(pkg, dst,
                                                download_cmd_template)
        except KeyboardInterrupt:
            printerr("Aborted")
            return 1

    # download package file from mirror if necessary
    if must_download:
        print(">> Downloading %s from mirror" % pkg)
        try:
            download_cmd = download_cmd_template.substitute(
                {'u': argv[1], 'o': argv[2]})
            return runcmd2(download_cmd)
        except KeyboardInterrupt:
            printerr("Aborted")
            return 1
    else:
        return 0


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--cache':
        sys.exit(cache_main(sys.argv))
    else:
        sys.exit(main(sys.argv))
