# !/usr/bin/env python

from distutils.core import setup
import time

setup(
    name='Pkgdistcache-client',
    version=time.strftime('%Y.%m.%d.%H.%M.%S', time.gmtime(1614290852.217266)),
    description='A distributed local-network cache for pacman packages.',
    author='Blx32',
    author_email='g@srmoura.com.br',
    license="GPL",
    long_description='A distributed local-network cache for pacman packages.',
    url='https://github.com/gabrielmoura/pkgdistcache',
    py_modules=['Pkgdistcache-client'],
)
setup(
    name='Pkgdistcache-daemon',
    version=time.strftime('%Y.%m.%d.%H.%M.%S', time.gmtime(1614290852.217266)),
    description='A distributed local-network cache for pacman packages.',
    author='Blx32',
    author_email='g@srmoura.com.br',
    license="GPL",
    long_description='A distributed local-network cache for pacman packages.',
    url='https://github.com/gabrielmoura/pkgdistcache',
    py_modules=['Pkgdistcache-daemon'],
)
