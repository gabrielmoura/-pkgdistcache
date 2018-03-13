# Contributor: Alessio Bianchi <venator85 at gmail dot com>
# Maintainer: Eric Anderson <ejona86@gmail.com>
# Maintainer: Gabriel Moura <g@srmoura.com.br>

pkgname=pkgdistcache
pkgver=0.4.5
pkgrel=2
pkgdesc='A distributed local-network cache for pacman packages and multipart using axel'
arch=('any')
url='https://github.com/gabrielmoura/pkgdistcache'
license=('GPL')
depends=('avahi' 'python-dbus' 'dbus-glib' 'python-gobject' 'curl' 'python-requests' 'axel' 'python-distutils-extra')
backup=(etc/pkgdistcache.conf)
source=(
 'pkgdistcache-client' 
 'Pkgdistcache-client.py'
 'pkgdistcache-daemon'
 'Pkgdistcache-daemon.py'
 'pkgdistcache.conf'
 'pkgdistcache.install'
 'pkgdistcached.service'
 'setup.py')

sha512sums=(
'SKIP'
 'efe54dc0f9647343a4cfb93bba102789480ece03bef49e49a0cf638c799c155bbfdbd68ec4e4b816b3d398d88e6bb4f49e577d488c162ec8a7ff9c9545075a74'
  'SKIP'
   '5e66f1f2332e6e230e51bba4ee9cdd0c8fe90da92d36dc05a68499a83e5996c5a3795b00dbd28a387bc92252478dfc76b57f5603020b5205bf3bde51526c082c'
   'b83b50597f490ef2fb2f1c2e8b3c82668f0063c403098c789afb8435bb3e5ffe7838b1ff9b6bbe35196db36054551c87703c6a6ffcae6231c7c0bdefe9f2c220'
   'ac2a426db2df116c5eb6500424d6c79fa6b1cd71493438a37de3169d1d7adeb726a80b2c5cd5713a0d54ff8e8f9dd89d4147c8e642cd1b6b84ae141e9e43f228'
   'SKIP'
   'e284c5f9b06090c0df3a475f2871d6c2565334ccedcca7de9f7bc44528b3e63faa15ae82f12497abe242e7a973ce3cf1997ebced582272bb68b6b8e69e3ba3c6')

validpgpkeys=('DDE43DEA10CA4EED5D7F881E76CE3619A00292AF') # Gabriel Moura <g@srmoura.com.br>

package() {
  install -d "${pkgdir}/usr/bin/"
  env python setup.py install --root="$pkgdir/" --optimize=1
  install -m755 "${srcdir}/pkgdistcache-client" "${pkgdir}/usr/bin/"
  install -m755 "${srcdir}/pkgdistcache-daemon" "${pkgdir}/usr/bin/"
  install -d "${pkgdir}/etc/"
  install -m644 "${srcdir}/pkgdistcache.conf" "${pkgdir}/etc/"
  install -d "${pkgdir}/usr/lib/systemd/system/"
  install -m644 "${srcdir}/pkgdistcached.service" \
      "${pkgdir}/usr/lib/systemd/system/"
}
install='pkgdistcache.install'