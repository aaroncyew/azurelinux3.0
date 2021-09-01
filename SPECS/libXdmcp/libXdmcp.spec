Summary:        X Display Manager Control Protocol library
Name:           libXdmcp
Version:        1.1.3
Release:        5%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://www.x.org
Source0:        https://www.x.org/pub/individual/lib/%{name}-%{version}.tar.bz2

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  xmlto
BuildRequires:  xorg-x11-proto-devel
BuildRequires:  xorg-x11-util-macros

%description
X Display Manager Control Protocol library.

%package devel
Summary:        Development files for %{name}

Requires:       %{name} = %{version}-%{release}

Provides:       pkgconfig(xdmcp) = %{version}-%{release}

%description devel
libXdmcp development package.

%prep
%autosetup

%build
autoreconf -v --install --force
%configure --disable-static
make V=1 %{?_smp_mflags}

%install

make install DESTDIR=%{buildroot} INSTALL="install -p"

# We intentionally don't ship *.la files
find %{buildroot} -type f -name "*.la" -delete -print

# manual fixup later
rm -rf %{buildroot}%{_docdir}

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license COPYING
%doc AUTHORS ChangeLog Wraphelp.README.crypto
%{_libdir}/libXdmcp.so.6
%{_libdir}/libXdmcp.so.6.0.0

%files devel
%doc README.md
%{_includedir}/X11/Xdmcp.h
%{_libdir}/libXdmcp.so
%{_libdir}/pkgconfig/xdmcp.pc

%changelog
* Thu Jan 14 2021 Vinicius Jarina <vinja@microsoft.com> - 1.1.3-5
- Initial CBL-Mariner import from Fedora 33 (license: MIT).
- License verified.

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Mar 20 2019 Adam Jackson <ajax@redhat.com> - 1.1.3-1
- libXdmcp 1.1.3

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jul 05 2018 Adam Jackson <ajax@redhat.com> - 1.1.2-11
- Drop useless %%defattr

* Fri Jun 29 2018 Adam Jackson <ajax@redhat.com> - 1.1.2-10
- Use ldconfig scriptlet macros

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Mar 28 2017 Benjamin Tissoires <benjamin.tissoires@redhat.com> 1.1.2-6
- Do not pull libbsd, use getentropy or getrandom syscall instead

* Wed Mar 01 2017 Benjamin Tissoires <benjamin.tissoires@redhat.com> 1.1.2-5
- Use libbsd for randoms (CVE-2017-2625, rhbz#1427716)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Mar 23 2015 Benjamin Tissoires <benjamin.tissoires@redhat.com> 1.1.2-1
- libXdmcp 1.1.2

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Mar 07 2013 Peter Hutterer <peter.hutterer@redhat.com> - 1.1.1-4
- autoreconf for aarch64

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Mar 08 2012 Adam Jackson <ajax@redhat.com> 1.1.1-1
- libXdmcp 1.1.1

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Nov 08 2010 Adam Jackson <ajax@redhat.com> 1.1.0-1
- libXdmcp 1.1.0

* Wed Oct 21 2009 Parag <paragn@fedoraproject.org> - 1.0.3-3
- Merge-Review #226068
- make is not verbose

* Thu Oct 08 2009 Parag <paragn@fedoraproject.org> - 1.0.3-2
- Merge-Review #226068
- Removed BR:pkgconfig
- Few spec cleanups.

* Thu Sep 24 2009 Peter Hutterer <peter.hutterer@redhat.com> 1.0.3-1
- libXdmcp 1.0.3
- libXdmcp-1.0.2-namespace-pollution.patch: drop

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 23 2009 Adam Jackson <ajax@redhat.com> 1.0.2-10
- Un-require xorg-x11-filesystem

* Thu Jul 23 2009 Adam Jackson <ajax@redhat.com> 1.0.2-9
- Remove useless %%dir

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Feb 21 2009 Adam Jackson <ajax@redhat.com> 1.0.2-7
- Merge review cleanups. (#226068)

* Tue Jul 15 2008 Adam Jackson <ajax@redhat.com> 1.0.2-6
- Fix license tag.

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.0.2-5
- Autorebuild for GCC 4.3

* Tue Aug 21 2007 Adam Jackson <ajax@redhat.com> - 1.0.2-4
- Rebuild for build id

* Sat Apr 21 2007 Matthias Clasen <mclasen@redhat.com> 1.0.2-3
- Don't install INSTALL

* Mon Nov 20 2006 Adam Jackson <ajax@redhat.com> 1.0.2-2.fc7
- libXdmcp-1.0.2-namespace-pollution.patch: Hide Xalloc and friends from the
  dynamic linker.

* Mon Nov 20 2006 Adam Jackson <ajax@redhat.com> 1.0.2-1
- Update to 1.0.2

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> 1.0.1-2.1
- rebuild

* Wed Jun 07 2006 Mike A. Harris <mharris@redhat.com> 1.0.1-2
- Added "BuildRequires: xorg-x11-proto-devel"
- Added "Requires: xorg-x11-proto-devel" to devel package, needed by xdmcp.pc
- Replace "makeinstall" with "make install DESTDIR=..."
- Remove package ownership of mandir/libdir/etc.

* Thu Apr 27 2006 Adam Jackson <ajackson@redhat.com> 1.0.1-1
- Update to 1.0.1

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.0.0-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.0.0-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan 23 2006 Mike A. Harris <mharris@redhat.com> 1.0.0-2
- Bumped and rebuilt

* Fri Dec 16 2005 Mike A. Harris <mharris@redhat.com> 1.0.0-1
- Updated libXdmcp to version 1.0.0 from X11R7 RC4

* Tue Dec 13 2005 Mike A. Harris <mharris@redhat.com> 0.99.2-1
- Updated libXdmcp to version 0.99.2 from X11R7 RC3
- Added "Requires(pre): xorg-x11-filesystem >= 0.99.2-3", to ensure
  that /usr/lib/X11 and /usr/include/X11 pre-exist.
- Removed 'x' suffix from manpage directories to match RC3 upstream.

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Nov 11 2005 Mike A. Harris <mharris@redhat.com> 0.99.1-2
- Changed 'Conflicts: XFree86-devel, xorg-x11-devel' to 'Obsoletes'
- Changed 'Conflicts: XFree86-libs, xorg-x11-libs' to 'Obsoletes'

* Fri Oct 21 2005 Mike A. Harris <mharris@redhat.com> 0.99.1-1
- Update to libXdmcp-0.99.1 from X11R7 RC1 release.

* Thu Sep 29 2005 Mike A. Harris <mharris@redhat.com> 0.99.0-3
- Renamed package to remove xorg-x11 from the name due to unanimous decision
  between developers.
- Use Fedora Extras style BuildRoot tag.
- Disable static library creation by default.
- Add missing defattr to devel subpackage
- Add missing documentation files to doc macro

* Tue Aug 23 2005 Mike A. Harris <mharris@redhat.com> 0.99.0-2
- Renamed package to prepend "xorg-x11" to the name for consistency with
  the rest of the X11R7 packages.
- Added "Requires: %%{name} = %%{version}-%%{release}" dependency to devel
  subpackage to ensure the devel package matches the installed shared libs.
- Added virtual "Provides: lib<name>" and "Provides: lib<name>-devel" to
  allow applications to use implementation agnostic dependencies.
- Added post/postun scripts which call ldconfig.
- Added Conflicts with XFree86-libs and xorg-x11-libs to runtime package,
  and Conflicts with XFree86-devel and xorg-x11-devel to devel package.

* Mon Aug 22 2005 Mike A. Harris <mharris@redhat.com> 0.99.0-1
- Initial build.
