%global bdftopcf 1.1
%global fonttosfnt 1.2.1
%global mkfontdir 1.0.7
%global mkfontscale 1.1.3
%global font_util 1.3.1
# Must be kept in sync with xorg-x11-fonts!
%global _x11fontdir %{_datadir}/X11/fonts
Summary:        X.Org X11 font utilities
Name:           xorg-x11-font-utils
Version:        7.5
Release:        50%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Azure Linux
URL:            https://www.x.org
Source0:        https://www.x.org/pub/individual/app/bdftopcf-%{bdftopcf}.tar.bz2
Source1:        https://www.x.org/pub/individual/app/fonttosfnt-%{fonttosfnt}.tar.bz2
Source2:        https://www.x.org/pub/individual/app/mkfontdir-%{mkfontdir}.tar.bz2
Source3:        https://www.x.org/pub/individual/app/mkfontscale-%{mkfontscale}.tar.bz2
Source4:        https://www.x.org/pub/individual/font/font-util-%{font_util}.tar.bz2
# helper script used in post for xorg-x11-fonts
Source5:        xorg-x11-fonts-update-dirs
Source6:        xorg-x11-fonts-update-dirs.1

Patch0:         mkfontscale-examine-all-encodings.patch

BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  pkg-config
BuildRequires:  zlib-devel
BuildRequires:  pkgconfig(fontenc)
BuildRequires:  freetype-devel
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xorg-macros) >= 1.8

Provides:       bdftopcf = %{bdftopcf}
Provides:       fonttosfnt = %{fonttosfnt}
Provides:       mkfontdir = %{mkfontdir}
Provides:       mkfontscale = %{mkfontscale}
Provides:       font-util = %{font_util}
Provides:       font-utils = %{version}-%{release}
Provides:       ucs2any = %{font_util}

%description
X.Org X11 font utilities required for font installation, conversion, and
generation.

%prep
%setup -q -c %{name}-%{version} -a1 -a2 -a3 -a4
pushd mkfontscale-*
%patch0 -p1 -b .all-encodings
popd

%build
# Build all apps
{
for app in * ; do
    pushd $app
        autoreconf -vif
        case $app in
            font-util-*)
                %configure --with-fontrootdir=%{_x11fontdir}
                ;;
            *)
                %configure
                ;;
        esac
        make %{?_smp_mflags}
    popd
done
}

%install
# Install all apps
{
    for app in * ; do
        pushd $app
            %make_install
        popd
    done
    for i in */README ; do
        [ -s $i ] && cp $i README-$(echo $i | sed 's/-[0-9].*//')
    done
    for i in */COPYING ; do
        grep -q stub $i || cp $i COPYING-$(echo $i | sed 's/-[0-9].*//')
    done
}

install -m 744 %{SOURCE5} %{buildroot}%{_bindir}/xorg-x11-fonts-update-dirs
sed -i "s:@DATADIR@:%{_datadir}:" %{buildroot}%{_bindir}/xorg-x11-fonts-update-dirs

install -m 744 -p -D %{SOURCE6} %{buildroot}%{_mandir}/man1/xorg-x11-fonts-update-dirs.1

find %{buildroot} -name bdftruncate\* -print0 | xargs -0 rm -f

%files
%doc README-* COPYING-bdftopcf COPYING-[c-z]*
%{_bindir}/bdftopcf
%{_bindir}/fonttosfnt
%{_bindir}/mkfontdir
%{_bindir}/mkfontscale
%{_bindir}/ucs2any
%{_bindir}/xorg-x11-fonts-update-dirs
%{_datadir}/aclocal/fontutil.m4
%{_libdir}/pkgconfig/fontutil.pc
%{_mandir}/man1/bdftopcf.1*
%{_mandir}/man1/fonttosfnt.1*
%{_mandir}/man1/mkfontdir.1*
%{_mandir}/man1/mkfontscale.1*
%{_mandir}/man1/ucs2any.1*
%{_mandir}/man1/xorg-x11-fonts-update-dirs.1*
%dir %{_x11fontdir}
%dir %{_x11fontdir}/util
%{_x11fontdir}/util/map-*

%changelog
* Fri Apr 22 2022 Olivia Crain <oliviacrain@microsoft.com> - 7.5-50
- Remove explicit pkgconfig provides that are now automatically generated by RPM

* Wed Oct 27 2021 Muhammad Falak <mwani@microsft.com> - 7.5-49
- Remove epoch

* Thu Jan 07 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1:7.5-48
- Initial CBL-Mariner import from Fedora 33 (license: MIT).
- License verified.
- Added explicit "Provides" for "pkgconfig(*)".
- Switched BR "pkgconfig(freetype2)" to "freetype-devel" available from core CBL-Mariner.

* Wed Dec 16 2020 Peter Hutterer <peter.hutterer@redhat.com> 1:7.5-47
- fonttosfnt 1.2.1

* Thu Nov  5 10:26:37 AEST 2020 Peter Hutterer <peter.hutterer@redhat.com> - 1:7.5-46
- Add BuildRequires for make

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-45
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jan 31 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-44
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Jan 06 2020 Peter Hutterer <peter.hutterer@redhat.com> 1:7.5-43
- fonttosfnt 1.1.0

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-42
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-41
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Aug 01 2018 Peter Hutterer <peter.hutterer@redhat.com> 1:7.5-40
- fonttosfnt 1.0.5

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-39
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu May 17 2018 Peter Hutterer <peter.hutterer@redhat.com> 1:7.5-38
- mkfontscale 1.1.3

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-37
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 25 2018 Adam Jackson <ajax@redhat.com> - 7.5-36
- bdftopcf 1.1

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-35
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-34
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-33
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Sep 28 2016 Hans de Goede <hdegoede@redhat.com> - 1:7.5-32
- bdftopcf 1.0.5

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:7.5-31
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 20 2016 Peter Hutterer <peter.hutterer@redhat.com>
- s/define/global/

* Thu Oct 15 2015 Adam Jackson <ajax@redhat.com> 7.5-30
- Drop bdftruncate utility, nothing in the OS uses it and we don't ship BDF
  fonts in any case.

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:7.5-29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri May 01 2015 Simone Caronni <negativo17@gmail.com> - 1:7.5-28
- font-util 1.3.1

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 1:7.5-27
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Sat Jan 17 2015 Simone Caronni <negativo17@gmail.com> - 1:7.5-26
- Update mkfontscale to 1.1.2.

* Mon Nov 10 2014 Simone Caronni <negativo17@gmail.com> - 1:7.5-25
- Restore font-utils provider, required by some packages for building.
 examine all platform=3 encodings (fixes #578460)
