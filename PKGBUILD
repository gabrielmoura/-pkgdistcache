# Contributor: Alessio Bianchi <venator85 at gmail dot com>
# Maintainer: Eric Anderson <ejona86@gmail.com>
# Maintainer: Gabriel Moura <g@srmoura.com.br>

pkgname=pkgdistcache
pkgver=0.5.10
pkgrel=1
pkgdesc='A distributed local-network cache for pacman packages and multipart using axel'
arch=('any')
url='https://github.com/gabrielmoura/pkgdistcache'
license=('GPL')
depends=('avahi' 'python-dbus' 'dbus-glib' 'python-gobject' 'curl' 'python-requests' 'axel' 'python-xdg' "python<=3.9.2")
makedepends=('python-setuptools' 'python-distutils-extra')
_python=python3.9
backup=(etc/pkgdistcache.conf)
#conflicts=('pkgdistcache')
#replaces=('pkgdistcache')
source=(
 'pkgdistcache-client' 
 'Pkgdistcache-client.py'
 'pkgdistcache-daemon'
 'Pkgdistcache-daemon.py'
 'pkgdistcache.conf'
 'pkgdistcache.install'
 'pkgdistcached.service'
 'setup.py')


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
 chmod 777 "${pkgdir}//usr/lib/${_python}/site-packages/Pkgdistcache-client.py"
 chmod 777 "${pkgdir}//usr/lib/${_python}/site-packages/Pkgdistcache-daemon.py"
  
}
install='pkgdistcache.install'
md5sums=('9db4918e3e8c693ad26687cf01a4012d'
         '9c41dbab42cd3db0d0ec9a5dfb77f290'
         'c0af9725c5e2ab5dd0462d4963a2536f'
         '27ba6a8d2efcb96be7037b6df5fab616'
         '18bac9300a7b5645f2211f582b4486c8'
         '1bde66d909303abb7816c8302821924a'
         'f4c4f04e80a0cfa85443e920d6d2a4a3'
         'ab9fb57ade6aa32ab032350548f26799')
sha512sums=('5b0dee1f7ed25e88036d050e156658088d1aec2f746656c81d5fcfa7bd1ed36557c19ab54da79b41a0dc964fc0fe13ebd32fb7456ce2d245e2776251ac7d620f'
            'be6f3c59f656e698e640b03634bea0c3a14c34091bb68ddfc742c09053eadc6a4f0833d9e4602ef66ce7ec91636341672cd75e000ba271f2c2cdc9e22f262ce2'
            'e0c2c79da2cba7e67447d9c0cae9a02c3a2083dbfd12470ee1bc572976f4d31e32b13b265f5303449a289fb9274ae0049c2bd2c2b73261093d5b30aa230983aa'
            'c1a9e66074d60e4b1e42534f5e0a21c19054b98822f389f287fd727e54d465c47d5d632ceb0ab4ad4115eac3da26202079ed79d7b753f6cfaef9a2dd8888c205'
            '6662b3ee9c41ff34c8b4fe3c057f3cc020051f9486c2365ebb280f7414a0c656b5a0eb4643df166ad20e023016b311eb51f6b0ab74d4d15891211e576f002ddf'
            'ac2a426db2df116c5eb6500424d6c79fa6b1cd71493438a37de3169d1d7adeb726a80b2c5cd5713a0d54ff8e8f9dd89d4147c8e642cd1b6b84ae141e9e43f228'
            'f69054877fa4c6ed808d2f7255943823554708122510e9ef27cfc4bca0afa1a43e7b6b973d205a9d8db74d1658368a21c6137305eb2a3a63240c277b3500f8dc'
            '502eca3d47c3a08c54b9f9eaf5932069f40e18b3a6e4d5c11743e4439d35970dfa2dfe281aff33bd57d9190c9b560fba63b9efd2d710320ad739e63bd13ae9b1')
