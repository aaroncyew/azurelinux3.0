Summary:        Libraries for the public client interface for NIS(YP) and NIS+.
Name:           libnsl2
Version:        2.0.0
Release:        1%{?dist}
Source0:        https://github.com/thkukuk/libnsl/archive/v%{version}/libnsl-%{version}.tar.gz
License:        BSD and GPLv2+
Group:          System Environment/Libraries
URL:            https://github.com/thkukuk/libnsl
Vendor:         Microsoft Corporation
Distribution:   Mariner
Requires:       libtirpc
Requires:       rpcsvc-proto
BuildRequires:  libtirpc-devel
BuildRequires:  rpcsvc-proto-devel

%description
The libnsl package contains the public client interface for NIS(YP) and NIS+.
It replaces the NIS library that used to be in glibc.

%package    devel
Summary:    Development files for the libnsl library
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}
Requires:   libtirpc-devel
Requires:   rpcsvc-proto-devel

%description    devel
This package includes header files and libraries necessary for developing programs which use the nsl library.

%prep
%setup -q -n libnsl-%{version}

%build
autoreconf -fi
%configure
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
find %{buildroot} -type f -name "*.la" -delete -print

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%files
%license COPYING
%{_libdir}/*.so
%{_libdir}/*.so.*

%files devel
%{_includedir}/rpcsvc/*
%{_libdir}/pkgconfig/*
%{_libdir}/*.a

%changelog
* Wed Jan 12 2022 Henry Li <lihl@microsoft.com> - 2.0.0-1
- Upgrade to version 2.0.0
- Modify Source0 field to use macros

* Fri Sep 10 2021 Thomas Crain <thcrain@microsoft.com> - 1.2.0-5
- Remove libtool archive files from final packaging

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 1.2.0-4
- Added %%license line automatically

*   Fri Apr 17 2020 Nicolas Ontiveros <niontive@microsoft.com> 1.2.0-3
-   Rename libnsl to libnsl2.
-   Remove sha1 macro.
-   License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 1.2.0-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
* Fri Sep 21 2018 Alexey Makhalov <amakhalov@vmware.com> 1.2.0-1
- Initial version
