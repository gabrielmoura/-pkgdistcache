#!/usr/bin/env python
# coding: utf-8
#
# pkgdistcache client v0.3.1
# by Alessio Bianchi <venator85@gmail.com>
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
import pickle
import requests

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


# Run a command synchronously, redirecting stdout and stderr to strings
def runcmd(cmd, cwd=None):
    pipe = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = pipe.communicate()  # wait for process to terminate and return stdout and stderr
    return {'stdout': stdout.strip(), 'stderr': stderr.strip(), 'retcode': pipe.returncode}


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
        return "(%s, %s, %s, %d)" % (self.service, self.host, self.ip, self.port)

    def __repr__(self):
        # il tostring sulle liste è repr
        return self.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        return hash(self) == hash(other)


class AvahiBrowser(object):
    def __init__(self):
        # Connect to the system bus...
        self.bus = dbus.SystemBus()
        # Get a proxy to the object we want to talk to.
        avahi_proxy = self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER)
        # Set the interface we want to use; server in this case.
        self.server = dbus.Interface(avahi_proxy, avahi.DBUS_INTERFACE_SERVER)
        self.version_string = self.server.GetVersionString()
        self.domain = "local"
        self.loop = gobject.MainLoop()
        self.services = []

    def browse(self, stype):
        # Ask the server for a path to the browser object for the service we're interested in...
        browser_path = self.server.ServiceBrowserNew(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, stype, self.domain,
                                                     dbus.UInt32(0))
        # Get it's proxy object...
        browser_proxy = self.bus.get_object(avahi.DBUS_NAME, browser_path)
        # And set the interface we want to use      
        browser = dbus.Interface(browser_proxy, avahi.DBUS_INTERFACE_SERVICE_BROWSER)

        # Now connect the call backs to the relevant signals.
        browser.connect_to_signal('ItemNew', self.new_service)
        browser.connect_to_signal('AllForNow', self.all_for_now)
        self.loop.run()
        return self.services

    def new_service(self, interface, protocol, name, stype, domain, flags):
        if flags & avahi.LOOKUP_RESULT_LOCAL:
            # The service is on this machine; ignore
            return
        try:
            s = self.server.ResolveService(interface, protocol, name, stype, domain, avahi.PROTO_UNSPEC, dbus.UInt32(0))
            service = Service(str(s[3]), str(s[2]), str(s[7]), int(s[8]))  # service name, host, ip, port
            self.services.append(service)
        except dbus.DBusException as ex:
            # Mainly expect to see org.freedesktop.Avahi.TimeoutError: Timeout reached
            printwarn(ex)

    def all_for_now(self):
        self.loop.quit()


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

    must_download = True
    if not (pkg.endswith('.db') or pkg.endswith('.db.sig')):
        # find first /tmp/pkgdistcache.* file modified less than CACHE_FILE_LIFE minutes ago
        cmd = 'find /tmp -name "pkgdistcache.*" -mmin -' + str(config['cache_file_life'])
        cache_file = runcmd(cmd)['stdout']
        if len(cache_file) > 0:
            # recent cache file found, use it
            with open(cache_file, 'rb') as f:
                pkgdistcache_clients = pickle.load(f)
        else:
            # recent cache file not found, discover other pkgdistcache capable hosts via avahi and save result to a new cache file
            runcmd("rm -f /tmp/pkgdistcache.*")  # remove any old cache file
            cache_file = runcmd('mktemp /tmp/pkgdistcache.XXXXX')['stdout']  # create new cache file

            hostname = runcmd('hostname')['stdout']
            browser = AvahiBrowser()
            clients = browser.browse("_pkgdistcache._tcp")
            clients = set(clients)  # remove duplicates (eg services offered on more than a network card etc.)
            pkgdistcache_clients = []
            for client in clients:
                if client.host != hostname:  # exclude current machine from results
                    pkgdistcache_clients.append(client)

            with open(cache_file, 'wb') as f:
                pickle.dump(pkgdistcache_clients, f, -1)

        if pkgdistcache_clients:
            print("-- Discovered hosts: %s" % ", ".join(set([c.host for c in pkgdistcache_clients])))
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
                printwarn("Failed checking host '%s' with ip '%s': %s" % (client.host, clientip, repr(e)))
                continue
            if r.status_code != 200:
                continue

            dst = argv[2]
            printmsg("Downloading %s from host '%s'" % (pkg, client.host))
            download_cmd = download_cmd_template.substitute({'u': url, 'o': dst})
            try:
                ret = runcmd2(download_cmd)
                if ret == 0:
                    must_download = False
                    break
                else:
                    printwarn("Host '%s' doesn't have %s in cache" % (client.host, pkg))
            except KeyboardInterrupt:
                printerr("Aborted")
                return 1

    # download package file from mirror if necessary
    if must_download == True:
        print(">> Downloading %s from mirror" % pkg)
        try:
            download_cmd = download_cmd_template.substitute({'u': argv[1], 'o': argv[2]})
            return runcmd2(download_cmd)
        except KeyboardInterrupt:
            printerr("Aborted")
            return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
