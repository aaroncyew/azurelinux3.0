Summary:        Glib interfaces to D-Bus API
Name:           dbus-glib
Version:        0.112
Release:        1%{?dist}
License:        AFL OR GPLv2+
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Libraries
URL:            https://dbus.freedesktop.org/doc/dbus-glib/
Source0:        https://dbus.freedesktop.org/releases/dbus-glib/%{name}-%{version}.tar.gz
BuildRequires:  dbus-devel
BuildRequires:  glib-devel
Requires:       dbus
Requires:       glib

%description
The D-Bus GLib package contains GLib interfaces to the D-Bus API.

%package        devel
Summary:        Libraries and headers for the D-Bus GLib bindings
Requires:       %{name} = %{version}
Requires:       dbus-devel
Requires:       glib-devel
Provides:       pkgconfig(dbus-glib-1)

%description devel
Headers and static libraries for the D-Bus GLib bindings

%prep
%autosetup

%build
%configure \
%if %{with_check}
    --enable-tests \
    --enable-asserts \
%endif
    --disable-static \
    --disable-gtk-doc
%make_build

%install
%make_install
find %{buildroot} -type f -name "*.la" -delete -print

%check
%make_build check

%ldconfig_scriptlets

%files
%defattr(-,root,root)
%license COPYING
%{_sysconfdir}/bash_completion.d/*
%{_bindir}/*
%{_libdir}/*.so.*
%{_libexecdir}/*
%{_mandir}/man1/*
%{_datadir}/gtk-doc/*

%files devel
%defattr(-,root,root)
%{_includedir}/dbus-1.0/dbus/*.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%changelog
* Thu Jan 20 2022 Nicolas Guibourge <nicolasg@microsoft.com> - 0.112-1
- Upgrade to 0.112

* Fri Sep 10 2021 Thomas Crain <thcrain@microsoft.com> - 0.110-5
- Remove libtool archive files from final packaging

* Thu Jun 17 2021 Thomas Crain <thcrain@microsoft.com> - 0.110-4
- Move pkgconfig(dbus-glib-1) provides to the devel package from the base package
- License verified- corrected to "AFL OR GPLv2+" from "AFL AND GPLv2+"
- Fix test suite by compiling unit tests, assertions during %%with_check builds
- Use configure/make macros
- Spec linted

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 0.110-3
- Added %%license line automatically

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> - 0.110-2
- Initial CBL-Mariner import from Photon (license: Apache2).

* Mon Sep 10 2018 Ajay Kaher <akaher@vmware.com> - 0.110-1
- Upgraded to 0.110

* Wed May 03 2017 Bo Gan <ganb@vmware.com> - 0.108-1
- Update to 0.108

* Wed Oct 05 2016 ChangLee <changlee@vmware.com> - 0.106-5
- Modified %check

* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 0.106-4
- GA - Bump release of all rpms

* Mon Feb 22 2016 XIaolin Li <xiaolinl@vmware.com> - 0.106-1
- Updated to version 0.106

* Thu Jan 28 2016 Anish Swaminathan <anishs@vmware.com> - 0.104-3
- Add requires to dbus-glib-devel

* Tue Sep 22 2015 Harish Udaiya Kumar <hudaiyakumar@vmware.com> - 0.104-2
- Updated build requires after creating devel package for dbus

* Tue Jun 23 2015 Divya Thaluru <dthaluru@vmware.com> - 0.104-1
- Initial build.
