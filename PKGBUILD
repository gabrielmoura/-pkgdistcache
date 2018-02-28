# Contributor: Alessio Bianchi <venator85 at gmail dot com>
# Maintainer: Eric Anderson <ejona86@gmail.com>
# Maintainer: Gabriel Moura <g@srmoura.com.br>

pkgname=pkgdistcache
pkgver=0.4.5
pkgrel=1
pkgdesc='A distributed local-network cache for pacman packages'
arch=('any')
url='https://github.com/gabrielmoura/pkgdistcache'
license=('GPL')
depends=('avahi' 'python-dbus' 'dbus-glib' 'python-gobject' 'curl' 'python-requests' 'axel')
source=(
 'pkgdistcache-client' 
 'pkgdistcache-daemon'
 'pkgdistcache.conf'
 'pkgdistcache.install'
 'pkgdistcached.service')

sha512sums=('cd3a9a7ae4ef4c262f62e97e3c442c9969608d76a601c605e792ec87ffa50f365a3e53177538bf9d276ac64e0165510bcbf1eb6d4752a58a5170a9cf91cd5143' '27046ff41975eaf9acc801cd9367c965d49e125e64f969afa35a9c3ef59e5d767d50dc36f9a2d7ec15723844f364b2c7ab2b6977991c89a4df006a61b4bd0ede' '82a114b84963f7c94fdb88591121d3a12f20f0af149c8ad9a60165907511c4973dd373121e514049e57dccad9938f2551d1557fefd1a44633007595ac43e1db2' 'd2580a23720c2b45b67b7c430a882317774e4c208a94d7a29a55a766f3ae1b8db65ef3b8dd97fd663750581b27aa2056e73dbec4375c5db78d01bf88313fba1a' '40766fe45a462d0087921702c22d31c3c94a9446fe5ca4b835bbeef23a66804d0bf6683d5ac4cebbab7f99d5faf62d85fc998a6d68e3696884cf9c20fa440f85')

install='pkgdistcache.install'
validpgpkeys=('DDE43DEA10CA4EED5D7F881E76CE3619A00292AF') # Gabriel Moura <g@srmoura.com.br>

package() {
  install -d "${pkgdir}/usr/bin/"
  install -m755 "${srcdir}/pkgdistcache-client" "${pkgdir}/usr/bin/"
  install -m755 "${srcdir}/pkgdistcache-daemon" "${pkgdir}/usr/bin/"
  install -d "${pkgdir}/etc/"
  install -m644 "${srcdir}/pkgdistcache.conf" "${pkgdir}/etc/"
  install -d "${pkgdir}/usr/lib/systemd/system/"
  install -m644 "${srcdir}/pkgdistcached.service" \
      "${pkgdir}/usr/lib/systemd/system/"
}