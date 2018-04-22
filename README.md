# PkgDistCache

### Um cache de rede local distribuído para pacotes pacman com multi conexões usando axel
Downlaod:
[Pacote](https://transfer.sh/AoIAp/pkgdistcache-0.5.0-4-any.pkg.tar.xz)
[Assinatura](https://transfer.sh/P3lnC/pkgdistcache-0.5.0-4-any.pkg.tar.xz.sig)

## Instalação

> 1. git clone https://github.com/gabrielmoura/pkgdistcache
> 2. cd pkgdistcache
> 3. makepkg
> 4. pacman -U pkgdistcache-0.5.1-4-any.pkg.tar.xz

## Configuração

Inicie o serviço servidor
> sudo systemctl enable --now pkgdistcached

Habilite o cliente

> sudo systemctl enable avahi-daemon

Edite /etc/pacman.conf e defina:
     
     XferCommand = /usr/bin/pkgdistcache-client %u %o

o deixando como unica opção XferCommand.
