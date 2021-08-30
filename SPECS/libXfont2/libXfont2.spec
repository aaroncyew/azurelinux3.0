Summary:        X.Org X11 libXfont2 runtime library
Name:           libXfont2
Version:        2.0.3
Release:        9%{?dist}
License:        BSD AND MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://www.x.org
Source0:        https://www.x.org/pub/individual/lib/%{name}-%{version}.tar.bz2

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  freetype-devel
BuildRequires:  libfontenc-devel
BuildRequires:  libtool
BuildRequires:  pkg-config
BuildRequires:  xorg-x11-util-macros
BuildRequires:  xorg-x11-xtrans-devel >= 1.0.3-3
BuildRequires:  pkgconfig(fontsproto)

%description
X.Org X11 libXfont2 runtime library

%package devel
Summary:        X.Org X11 libXfont2 development package

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libfontenc-devel%{?_isa}

Provides:       pkgconfig(xfont2) = %{version}-%{release}

%description devel
X.Org X11 libXfont development package

%prep
%autosetup

%build
autoreconf -v --install --force
export CFLAGS="%{optflags} -Os"
%configure --disable-static
make %{?_smp_mflags}

%install
%make_install

# We intentionally don't ship *.la files
find %{buildroot} -type f -name "*.la" -delete -print

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license COPYING
%doc AUTHORS README ChangeLog
%{_libdir}/libXfont2.so.2*

%files devel
%{_includedir}/X11/fonts/libxfont2.h
%{_libdir}/libXfont2.so
%{_libdir}/pkgconfig/xfont2.pc

%changelog
* Fri Jan 15 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0.3-9
- Initial CBL-Mariner import from Fedora 33 (license: MIT).
- License verified.
- Added explicit "Provides" for "pkgconfig(*)".
- Replaced ldconfig scriptlets with explicit calls to ldconfig.

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Mar 21 2019 Adam Jackson <ajax@redhat.com> - 2.0.3-5
- Rebuild for xtrans 1.4.0

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 29 2018 Adam Jackson <ajax@redhat.com> - 2.0.3-2
- Use ldconfig scriptlet macros

* Mon Feb 26 2018 Benjamin Tissoires <benjamin.tissoires@redhat.com> 2.0.3-1
- libXfont 2.0.3 (CVE-2017-16611)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Oct 11 2017 Adam Jackson <ajax@redhat.com> - 2.0.2-1
- libXfont 2.0.2

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Sep 28 2016 Hans de Goede <hdegoede@redhat.com> - 2.0.1-2
- Add some fixes from upstream git master

* Wed Jun 08 2016 Adam Jackson <ajax@redhat.com> - 2.0.2-1
- Initial packaging forked from libXfont
