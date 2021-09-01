Summary:        epoxy runtime library
Name:           libepoxy
Version:        1.5.5
Release:        3%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://github.com/anholt/libepoxy
Source0:        %{url}/releases/download/%{version}/%{name}-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  libEGL-devel
BuildRequires:  libGL-devel
BuildRequires:  libX11-devel
BuildRequires:  mesa-dri-drivers
BuildRequires:  meson
BuildRequires:  pkg-config
BuildRequires:  python3
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(glesv2)

%description
A library for handling OpenGL function pointer management.

%package devel
Summary:        Development files for libepoxy

Requires:       %{name}%{?_isa} = %{version}-%{release}

Provides:       pkgconfig(epoxy) = %{version}-%{release}

%description devel
This package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -p1

%build
%meson
%meson_build

%install
%meson_install

%check
# This should be %%meson_test but the macro expands with a multiple
# embedded newlines for no obvious reason
ninja -C %{_vpath_builddir} test || \
    (cat %{_vpath_builddir}/meson-logs/testlog.txt ; exit 1)

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license COPYING
%doc README.md
%{_libdir}/libepoxy.so.0*

%files devel
%{_includedir}/epoxy/
%{_libdir}/libepoxy.so
%{_libdir}/pkgconfig/epoxy.pc

%changelog
* Mon Aug 30 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.5.5-2
- Removing BR on 'marinerui-rpm-macros'. Using macros from the build env.

* Mon Jan 11 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.5.5-1
- Initial CBL-Mariner import from Fedora 33 (license: MIT).
- License verified.
- Added BR for 'marinerui-rpm-macros'.
- Added explicit "Provides" for "pkgconfig(*)".
- Replaced ldconfig scriptlets with explicit calls to ldconfig.
- Skipping package tests with dependency on X11 to remove the 'xorg-x11-server-Xvfb' BR.

* Tue Jan 05 2021 Kalev Lember <klember@redhat.com> - 1.5.5-1
- Update to 1.5.5

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Nov 27 2019 Kalev Lember <klember@redhat.com> - 1.5.4-1
- Update to 1.5.4

* Fri Oct 25 2019 Peter Robinson <pbrobinson@gmail.com> - 1.5.3-5
- Rebuild for libglvnd 1.2, drop work-arounds

* Thu Aug 22 2019 Rex Dieter <rdieter@fedoraproject.org> - 1.5.3-4
- epoxy.pc: -Requires.private: gl egl (#1744320)

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Oct 05 2018 Kalev Lember <klember@redhat.com> - 1.5.3-1
- Update to 1.5.3

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Sun May 20 2018 Kalev Lember <klember@redhat.com> - 1.5.2-1
- Update to 1.5.2

* Wed Apr 25 2018 Adam Jackson <ajax@redhat.com> - 1.5.1-2
- Enable tests for all arches
- Run tests against Xvfb so we get plausible amounts of coverage

* Wed Apr 25 2018 Kalev Lember <klember@redhat.com> - 1.5.1-1
- Update to 1.5.1

* Wed Feb 28 2018 Kalev Lember <klember@redhat.com> - 1.5.0-1
- Update to 1.5.0

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.4.3-5
- Switch to %%ldconfig_scriptlets

* Fri Sep 22 2017 Adam Jackson <ajax@redhat.com> - 1.4.3-4
- Backport some useful bits from master

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul 13 2017 Adam Jackson <ajax@redhat.com> - 1.4.3-1
- libepoxy 1.4.3

* Thu Mar 09 2017 Igor Gnatenko <ignatenko@redhat.com> - 1.4.1-2
- Switch to meson
- Add license file
- Simplify spec

* Thu Mar 09 2017 Dave Airlie <airlied@redhat.com> - 1.4.1-1
- libepoxy 1.4.1

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Sep 23 2016 Adam Jackson <ajax@redhat.com> - 1.3.1-3
- Fix detection of EGL client extensions

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Nov 05 2015 Adam Jackson <ajax@redhat.com> 1.3.1-1
- libepoxy 1.3.1

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 05 2015 Dave Airlie <airlied@redhat.com> 1.2-3
- update GL registry files (add new EGL extension)

* Wed Mar 25 2015 Adam Jackson <ajax@redhat.com> 1.2-2
- Fix description to not talk about DRM
- Sync some small bugfixes from git

* Mon Oct 13 2014 Peter Robinson <pbrobinson@fedoraproject.org> 1.2.0-1
- Update to 1.2 GA
- Don't fail build on make check failure for some architectures

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-0.4.20140411git6eb075c
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-0.3.20140411git6eb075c
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Apr 11 2014 Dave Airlie <airlied@redhat.com> 1.2-0.2.20140411git6eb075c
- update to latest git snapshot

* Thu Mar 27 2014 Dave Airlie <airlied@redhat.com> 1.2-0.1.20140307gitd4ad80f
- initial git snapshot
