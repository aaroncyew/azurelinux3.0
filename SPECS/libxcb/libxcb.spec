Summary:        A C binding to the X11 protocol
Name:           libxcb
Version:        1.13.1
Release:        6%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://xcb.freedesktop.org/
Source0:        https://xcb.freedesktop.org/dist/%{name}-%{version}.tar.bz2
# This is taken straight from the pthread-stubs source:
# http://cgit.freedesktop.org/xcb/pthread-stubs/blob/?id=6900598192bacf5fd9a34619b11328f746a5956d
# we don't need the library because glibc has working pthreads, but we need
# the pkgconfig file so libs that link against libxcb know this...
Source1:        pthread-stubs.pc.in

BuildRequires:  libtool
BuildRequires:  libxslt
BuildRequires:  pkg-config
BuildRequires:  python3
BuildRequires:  python3-devel
BuildRequires:  pkgconfig(xau) >= 0.99.2
BuildRequires:  pkgconfig(xcb-proto) >= 1.13
BuildRequires:  pkgconfig(xorg-macros) >= 1.18

%description
The X protocol C-language Binding (XCB) is a replacement for Xlib featuring a
small footprint, latency hiding, direct access to the protocol, improved
threading support, and extensibility.

%package devel
Summary:        Development files for %{name}

Requires:       %{name}%{?_isa} = %{version}-%{release}

Provides:       pkgconfig(pthread-stubs) = %{version}-%{release}
Provides:       pkgconfig(xcb) = %{version}-%{release}
Provides:       pkgconfig(xcb-composite) = %{version}-%{release}
Provides:       pkgconfig(xcb-damage) = %{version}-%{release}
Provides:       pkgconfig(xcb-dpms) = %{version}-%{release}
Provides:       pkgconfig(xcb-dri2) = %{version}-%{release}
Provides:       pkgconfig(xcb-dri3) = %{version}-%{release}
Provides:       pkgconfig(xcb-glx) = %{version}-%{release}
Provides:       pkgconfig(xcb-present) = %{version}-%{release}
Provides:       pkgconfig(xcb-randr) = %{version}-%{release}
Provides:       pkgconfig(xcb-record) = %{version}-%{release}
Provides:       pkgconfig(xcb-render) = %{version}-%{release}
Provides:       pkgconfig(xcb-res) = %{version}-%{release}
Provides:       pkgconfig(xcb-screensaver) = %{version}-%{release}
Provides:       pkgconfig(xcb-shape) = %{version}-%{release}
Provides:       pkgconfig(xcb-shm) = %{version}-%{release}
Provides:       pkgconfig(xcb-sync) = %{version}-%{release}
Provides:       pkgconfig(xcb-xf86dri) = %{version}-%{release}
Provides:       pkgconfig(xcb-xfixes) = %{version}-%{release}
Provides:       pkgconfig(xcb-xinerama) = %{version}-%{release}
Provides:       pkgconfig(xcb-xinput) = %{version}-%{release}
Provides:       pkgconfig(xcb-xkb) = %{version}-%{release}
Provides:       pkgconfig(xcb-xselinux) = %{version}-%{release}
Provides:       pkgconfig(xcb-xtest) = %{version}-%{release}
Provides:       pkgconfig(xcb-xv) = %{version}-%{release}
Provides:       pkgconfig(xcb-xvmc) = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for developing
applications that use %{name}.

%prep
%autosetup -p1

%build
sed -i 's/pthread-stubs //' configure.ac
# autoreconf -f needed to expunge rpaths
autoreconf -v -f --install
%configure \
    --disable-silent-rules \
    --disable-static \
    --disable-xprint \
    --enable-devel-docs=no \
    --enable-selinux \
    --enable-xinput \
    --enable-xkb

# Remove rpath from libtool (extra insurance if autoreconf is ever dropped)
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
sed 's,@libdir@,%{_libdir},;s,@prefix@,%{_prefix},;s,@exec_prefix@,%{_exec_prefix},' %{SOURCE1} \
    > %{buildroot}%{_libdir}/pkgconfig/pthread-stubs.pc

find %{buildroot} -type f -name "*.la" -delete -print

# Removing docs generated despite the "--enable-devel-docs=no" switch.
rm -r %{buildroot}/usr/share/doc/libxcb/tutorial

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%{_libdir}/libxcb-composite.so.0*
%{_libdir}/libxcb-damage.so.0*
%{_libdir}/libxcb-dpms.so.0*
%{_libdir}/libxcb-dri2.so.0*
%{_libdir}/libxcb-dri3.so.0*
%{_libdir}/libxcb-glx.so.0*
%{_libdir}/libxcb-present.so.0*
%{_libdir}/libxcb-randr.so.0*
%{_libdir}/libxcb-record.so.0*
%{_libdir}/libxcb-render.so.0*
%{_libdir}/libxcb-res.so.0*
%{_libdir}/libxcb-screensaver.so.0*
%{_libdir}/libxcb-shape.so.0*
%{_libdir}/libxcb-shm.so.0*
%{_libdir}/libxcb-sync.so.1*
%{_libdir}/libxcb-xf86dri.so.0*
%{_libdir}/libxcb-xfixes.so.0*
%{_libdir}/libxcb-xinerama.so.0*
%{_libdir}/libxcb-xinput.so.0*
%{_libdir}/libxcb-xkb.so.1*
%{_libdir}/libxcb-xselinux.so.0*
%{_libdir}/libxcb-xtest.so.0*
%{_libdir}/libxcb-xv.so.0*
%{_libdir}/libxcb-xvmc.so.0*
%{_libdir}/libxcb.so.1*

%files devel
%{_includedir}/xcb
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/*.3*

%changelog
* Thu Jan 07 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.13.1-6
- Initial CBL-Mariner import from Fedora 33 (license: MIT).
- License verified.
- Added explicit "Provides" for "pkgconfig(*)".
- Removed the "*-doc" subpackage to remove BRs on "doxygen" and "graphviz".
- Removed the "%%ldconfig_post(un)" macros.

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.13.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.13.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.13.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.13.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Sep 28 2018 Adam Jackson <ajax@redhat.com> - 1.13.1-1
- libxcb 1.13.1

* Tue Aug 14 2018 Adam Jackson <ajax@redhat.com> - 1.13-5
- Spec cleanup

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.13-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 29 2018 Adam Jackson <ajax@redhat.com> - 1.13-3
- Use ldconfig scriptlet macros

* Mon Mar 19 2018 Adam Jackson <ajax@redhat.com> - 1.13-2
- Build with python3

* Mon Mar 05 2018 Adam Jackson <ajax@redhat.com> - 1.13-1
- libxcb 1.13

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.12-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.12-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.12-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Jan 18 2017 Merlin Mathesius <mmathesi@redhat.com> - 1.12-2
- Add BuildRequires: python to fix FTBFS (BZ#1414586).

* Wed May 18 2016 Adam Jackson <ajax@redhat.com> - 1.12-1
- libxcb 1.12

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.11.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Sep 21 2015 Adam Jackson <ajax@redhat.com> 1.11.1-1
- libxcb 1.11.1

* Thu Jun 25 2015 Rex Dieter <rdieter@fedoraproject.org> 1.11-8
- followup fix for thread deadlocks (#1193742, fdo#84252)

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.11-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Jun 12 2015 Rex Dieter <rdieter@fedoraproject.org> 1.11-6
- pull in (partial?) upstream fix for deadlocks (#1193742, fdo#84252)

* Wed May 20 2015 Rex Dieter <rdieter@fedoraproject.org> - 1.11-5
- fix rpath harder (#1136546)
- %%build: --disable-silent-rules

* Tue May 19 2015 Rex Dieter <rdieter@fedoraproject.org> - 1.11-4
- fix fpath (use autoreconf -f)
- -devel: tighten deps via %%{?_isa}, drop Requires: pkgconfig (add explicit BR: pkgconfig)

* Thu Jan 08 2015 Simone Caronni <negativo17@gmail.com> - 1.11-3
- Clean up SPEC file, fix rpmlint warnings.
- Enable XInput extension (#1177701).

* Fri Oct 24 2014 Dan Horák <dan@danny.cz> - 1.11-2
- rebuilt for broken koji db - no buildroot info

* Wed Oct 01 2014 Adam Jackson <ajax@redhat.com> 1.11-1
- libxcb 1.11

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Jan 27 2014 Adam Jackson <ajax@redhat.com> 1.10-1
- libxcb 1.10 plus one. Updated ABIs: sync, xkb. New libs: dri3, present.

* Tue Aug  6 2013 Ville Skyttä <ville.skytta@iki.fi> - 1.9.1-3
- Install docs to %%{_pkgdocdir} where available.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri May 31 2013 Peter Hutterer <peter.hutterer@redhat.com> 1.9.1-1
- libxcb 1.9.1

* Fri May 24 2013 Peter Hutterer <peter.hutterer@redhat.com> 1.9-3
- Fix integer overflow in read_packet (CVE-2013-2064)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Oct 16 2012 Adam Jackson <ajax@redhat.com> 1.9-1
- libxcb 1.9

* Tue Sep 04 2012 Adam Jackson <ajax@redhat.com> 1.8.1-4
- --enable-xkb for weston
- --disable-xprint instead of manual rm
- BuildRequire an updated xcb-proto for XKB and DRI2 fixes

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Apr 09 2012 Adam Jackson <ajax@redhat.com> 1.8.1-1
- libxcb 1.8.1

* Fri Jan 13 2012 Adam Jackson <ajax@redhat.com> 1.8-2
- Don't %%doc in the base package, that pulls in copies of things we only
  want in -doc subpackage.

* Wed Jan 11 2012 Adam Jackson <ajax@redhat.com> 1.8-1
- libxcb 1.8
