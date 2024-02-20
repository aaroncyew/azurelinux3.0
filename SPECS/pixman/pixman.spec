Summary:        Pixel manipulation library
Name:           pixman
Version:        0.42.2
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Azure Linux
URL:            https://gitlab.freedesktop.org/pixman/pixman
Source0:        https://xorg.freedesktop.org/archive/individual/lib/%{name}-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  meson

%description
Pixman is a pixel manipulation library for X and Cairo.

%package devel
Summary:        Pixel manipulation library development package

Requires:       %{name}%{?isa} = %{version}-%{release}
Requires:       pkg-config

%description devel
Development library for pixman.

%prep
%autosetup -p1
# Bump up the test suite timeout because arm
sed -i 's/120/600/' test/meson.build

%build
%meson --auto-features=auto \
%ifarch %{arm}
  -Diwmmxt=disabled -Diwmmxt2=false \
%endif
  %{nil}

%meson_build

%install
%meson_install

%check
%meson_test

%ldconfig_scriptlets

%files
%license COPYING
%{_libdir}/libpixman-1*.so.*

%files devel
%dir %{_includedir}/pixman-1
%{_includedir}/pixman-1/pixman.h
%{_includedir}/pixman-1/pixman-version.h
%{_libdir}/libpixman-1*.so
%{_libdir}/pkgconfig/pixman-1.pc

%changelog
* Mon Nov 14 2022 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 0.42.2-1
- Auto-upgrade to 0.42.2 - CVE-2022-44638

* Fri Apr 22 2022 Olivia Crain <oliviacrain@microsoft.com> - 0.40.0-5
- Remove explicit pkgconfig provides that are now automatically generated by RPM

* Mon Aug 30 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 0.40.0-4
- Switching back to using ldconfig scriptlets, since they are now available.
- Removing BR on 'marinerui-rpm-macros'. Using macros from the build env.

* Fri Jan 15 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 0.40.0-3
- Initial CBL-Mariner import from Fedora 33 (license: MIT). Switched from Photon's spec.
- License verified.
- Added build-time dependency on "marinerui-rpm-macros".
- Added explicit "Provides" for "pkgconfig(*)".
- Replaced ldconfig scriptlets with explicit calls to ldconfig.

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.40.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Apr 20 2020 Kalev Lember <klember@redhat.com> - 0.40.0-1
- Update to 0.40.0

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.38.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Sep 09 2019 Kalev Lember <klember@redhat.com> - 0.38.4-1
- Update to 0.38.4

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.38.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Feb 12 2019 Kalev Lember <klember@redhat.com> - 0.38.0-1
- Update to 0.38.0
- Switch to the meson build system

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.36.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Nov 29 2018 Adam Jackson <ajax@redhat.com> - 0.36.0-1
- pixman 0.36.0

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.34.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 29 2018 Adam Jackson <ajax@redhat.com> - 0.34.0-9
- Use ldconfig scriptlet macros

* Fri May 04 2018 Dan Horák <dan[at]danny.cz> - 0.34.0-8
- fix vector loads in VMX (ppc64le) (#1572540)

* Thu Apr 26 2018 Adam Jackson <ajax@redhat.com> - 0.34.0-7
- Enable %%check
- --disable-vmx to fix %%check failures with gcc8
- Remove stray --disable-ssse3

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.34.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.34.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.34.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.34.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.34.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Feb 01 2016 <oded.gabbay@gmail.com> - 0.34.0-1
- Update to 0.34.0 (#1249357)

* Tue Dec 22 2015 Oded Gabbay <oded.gabbay@gmail.com> 0.33.6-1
- pixman 0.33.6

* Fri Oct 23 2015 Oded Gabbay <oded.gabbay@gmail.com> 0.33.4-1
- pixman 0.33.4

* Sun Aug 09 2015 Oded Gabbay <oded.gabbay@gmail.com> 0.33.2-1
- pixman 0.33.2
- Enable VMX fast paths on ppc64le now that they are fixed

* Tue Jun 16 2015 Peter Robinson <pbrobinson@fedoraproject.org> 0.32.6-6
- revert cflag option added in -5 the broke building

* Mon May 11 2015 Adam Jackson <ajax@redhat.com> 0.32.6-5
- Fix devel's requirement on the base package to include %%{?isa}

* Mon Nov 10 2014 Adam Jackson <ajax@redhat.com> 0.32.6-4
- Disable (broken) VMX fast paths on ppc64le for now.

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.32.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jul 11 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.32.6-2
- Enable make check but don't (currently) fail the build on failure
- Include COPYING as per packaging guidelines
- Minor spec cleanups

* Sun Jul 06 2014 Soren Sandmann <soren.sandmann@gmail.com> 0.32.6-1
- pixman 0.32.6
- drop SSSE3 patch

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.32.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Nov 14 2013 Soren Sandmann <ssp@redhat.com> 0.32.0-2
- Add patch to fix SSSE3 detection

* Sun Nov 10 2013 Soren Sandmann <ssp@redhat.com> 0.32.0-1
- pixman 0.32.0

* Sat Nov 2 2013 Soren Sandmann <ssp@redhat.com> 0.31.2-1
- pixman 0.31.2

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.30.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jul 04 2013 Karsten Hopp <karsten@redhat.com> 0.30.0-2
- bump release and rebuild to fix dependencies on PPC

* Wed May 8 2013 Soren Sandmann <ssp@redhat.com> 0.30.0-1
- pixman 0.30.0
