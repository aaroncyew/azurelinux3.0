Summary:        NUMA support for Linux
Name:           numactl
Version:        2.0.13
Release:        4%{?dist}
License:        GPLv2
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Base
URL:            https://github.com/numactl/numactl
Source0:        https://github.com/numactl/numactl/releases/download/v%{version}/%{name}-%{version}.tar.gz

%description
Simple NUMA policy support. It consists of a numactl program to run other programs with a specific NUMA policy.

%package -n libnuma
Summary:        Development libraries and header files for numactl
License:        LGPLv2.1
Requires:       %{name} = %{version}-%{release}
Provides:       %{name}-libs = %{version}-%{release}

%description -n libnuma
libnuma shared library ("NUMA API") to set NUMA policy in applications.

%package -n libnuma-devel
Summary:        Development libraries and header files for libnuma
License:        GPLv2
Requires:       %{name} = %{version}-%{release}
Provides:       %{name}-devel = %{version}-%{release}

%description -n libnuma-devel
The package contains libraries and header files for
developing applications that use libnuma.

%prep
%setup -q

%build
autoreconf -fiv
%configure --disable-static
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install

%check
make %{?_smp_mflags} check

%post -n libnuma  -p /sbin/ldconfig
%postun -n libnuma -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license LICENSE.GPL2
%{_bindir}/*
%{_mandir}/man8/*

%files -n libnuma
%defattr(-,root,root)
%{_libdir}/*.so.*

%files -n libnuma-devel
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/pkgconfig/numa.pc
%{_mandir}/man2/*
%{_mandir}/man3/*

%changelog
* Thu Dec 10 2020 Joe Schmitt <joschmit@microsoft.com> - 2.0.13-4
- Provide numactl-libs and numactl-devel.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 2.0.13-3
- Added %%license line automatically

*  Mon Jan 20 2020 Suresh Babu Chalamalasetty <schalam@microsoft.com> 2.0.13-2
-  Initial CBL-Mariner import from Photon (license: Apache2).

*  Mon Nov 18 2019 Alexey Makhalov <amakhalov@vmware.com> 2.0.13-1
-  Initial build. First version
