# Contributor: Alessio Bianchi <venator85 at gmail dot com>
# Maintainer: Eric Anderson <ejona86@gmail.com>
# Maintainer: Gabriel Moura <g@srmoura.com.br>

pkgname=pkgdistcache
pkgver=0.5.0
pkgrel=3
pkgdesc='A distributed local-network cache for pacman packages and multipart using axel'
arch=('any')
url='https://github.com/gabrielmoura/pkgdistcache'
license=('GPL')
depends=('avahi' 'python-dbus' 'dbus-glib' 'python-gobject' 'curl' 'python-requests' 'axel' 'python-xdg')
makedepends=('python2-setuptools' 'python-distutils-extra')
backup=(etc/pkgdistcache.conf)
conflicts=('pkgdistcache')
replaces=('pkgdistcache')
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
'5b0dee1f7ed25e88036d050e156658088d1aec2f746656c81d5fcfa7bd1ed36557c19ab54da79b41a0dc964fc0fe13ebd32fb7456ce2d245e2776251ac7d620f'
 'be6f3c59f656e698e640b03634bea0c3a14c34091bb68ddfc742c09053eadc6a4f0833d9e4602ef66ce7ec91636341672cd75e000ba271f2c2cdc9e22f262ce2'
  'e0c2c79da2cba7e67447d9c0cae9a02c3a2083dbfd12470ee1bc572976f4d31e32b13b265f5303449a289fb9274ae0049c2bd2c2b73261093d5b30aa230983aa'
  'e7ce06d2b84aa563981ee7faa0b44278a3dd26f53450969ed292a838acc6244078d4896c20b5c4989b6a9bb070508b66887c7092a44169d192a2fd9643a3de6f'
  'e17e6f23ad9b288c1d269f4305b9a92aca4f98b4c40330fac8a6e5e9840272c8a7a95c05aac64fd970923c99c8aa224491ff016480f221e11ee7d57722b393a3'
   'ac2a426db2df116c5eb6500424d6c79fa6b1cd71493438a37de3169d1d7adeb726a80b2c5cd5713a0d54ff8e8f9dd89d4147c8e642cd1b6b84ae141e9e43f228'
   'f69054877fa4c6ed808d2f7255943823554708122510e9ef27cfc4bca0afa1a43e7b6b973d205a9d8db74d1658368a21c6137305eb2a3a63240c277b3500f8dc'
   '725666d1a5714cbbb4250b2f03e303bad959b50f81bc522c28615aa8aedeec3fbf4f2284e08bfff5305d39d87780fa62a37b76943afd253ccfa240b387b6d502')

validpgpkeys=('DDE43DEA10CA4EED5D7F881E76CE3619A00292AF') # Gabriel Moura <g@srmoura.com.br>

package() {
  env python setup.py install --root="$pkgdir/" --optimize=1
   install -d "${pkgdir}/usr/bin/"
  install -m755 "${srcdir}/pkgdistcache-client" "${pkgdir}/usr/bin/"
  install -m755 "${srcdir}/pkgdistcache-daemon" "${pkgdir}/usr/bin/"
  install -d "${pkgdir}/etc/"
  install -m644 "${srcdir}/pkgdistcache.conf" "${pkgdir}/etc/"
  install -d "${pkgdir}/usr/lib/systemd/system/"
  install -m644 "${srcdir}/pkgdistcached.service" \
      "${pkgdir}/usr/lib/systemd/system/"
}
install='pkgdistcache.install'