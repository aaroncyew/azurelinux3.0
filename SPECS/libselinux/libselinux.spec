%{!?python2_sitelib: %global python2_sitelib %(python2 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}
%{!?python3_sitelib: %global python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib;print(get_python_lib())")}
Summary:        SELinux library and simple utilities
Name:           libselinux
Version:        2.9
Release:        4%{?dist}
License:        Public Domain
Group:          System Environment/Libraries
URL:            https://github.com/SELinuxProject/selinux/wiki
Source0:        https://github.com/SELinuxProject/selinux/releases/download/20190315/%{name}-%{version}.tar.gz
Vendor:         Microsoft Corporation
Distribution:   Mariner
BuildRequires:  libsepol-devel
BuildRequires:  pcre-devel, swig
BuildRequires:  python2-devel
BuildRequires:  python3-devel
Requires:       pcre-libs
Requires:       libsepol

%description
Security-enhanced Linux is a feature of the Linux® kernel and a number
of utilities with enhanced security functionality designed to add
mandatory access controls to Linux.  The Security-enhanced Linux
kernel contains new architectural components originally developed to
improve the security of the Flask operating system. These
architectural components provide general support for the enforcement
of many kinds of mandatory access control policies, including those
based on the concepts of Type Enforcement®, Role-based Access
Control, and Multi-level Security.

libselinux provides an API for SELinux applications to get and set
process and file security contexts and to obtain security policy
decisions.  Required for any applications that use the SELinux API.

%package        utils
Summary:        SELinux libselinux utilies
Group:          Development/Libraries
Requires:       libselinux = %{version}-%{release}

%description    utils
The libselinux-utils package contains the utilities

%package        devel
Summary:        Header files and libraries used to build SELinux
Group:          Development/Libraries
Requires:       libselinux = %{version}-%{release}
Requires:       pcre-devel
Requires:       libsepol-devel
Provides:       pkgconfig(libselinux)

%description    devel
The libselinux-devel package contains the libraries and header files
needed for developing SELinux applications.

%package        python
Summary:        SELinux python2 bindings for libselinux
Group:          Development/Libraries
Requires:       libselinux = %{version}-%{release}
Requires:       python2
Requires:       python2-libs

%description    python
The libselinux-python package contains the python2 bindings for developing
SELinux applications.

%package        python3
Summary:        SELinux python3 bindings for libselinux
Group:          Development/Libraries
Provides:       python3-%{name} = %{version}-%{release}
Requires:       libselinux = %{version}-%{release}
Requires:       python3
Requires:       python3-libs

%description    python3
The libselinux-python package contains the python3 bindings for developing
SELinux applications.

%prep
%setup -qn %{name}-%{version}

%build
sed '/unistd.h/a#include <sys/uio.h>' -i src/setrans_client.c
make clean
make %{?_smp_mflags} swigify CFLAGS="%{build_cflags} -Wno-error=strict-overflow"
make LIBDIR="%{_libdir}" %{?_smp_mflags} PYTHON=/usr/bin/python2 pywrap
make LIBDIR="%{_libdir}" %{?_smp_mflags} PYTHON=/usr/bin/python3 pywrap

%install
make DESTDIR="%{buildroot}" LIBDIR="%{_libdir}" SHLIBDIR="/%{_lib}" BINDIR="%{_bindir}" SBINDIR="%{_sbindir}" PYTHON=/usr/bin/python2 install install-pywrap

make DESTDIR="%{buildroot}" LIBDIR="%{_libdir}" SHLIBDIR="/%{_lib}" BINDIR="%{_bindir}" SBINDIR="%{_sbindir}" PYTHON=/usr/bin/python3 install install-pywrap

mkdir -p %{buildroot}/%{_prefix}/lib/tmpfiles.d
mkdir -p %{buildroot}/var/run/setrans
echo "d /var/run/setrans 0755 root root" > %{buildroot}/%{_prefix}/lib/tmpfiles.d/libselinux.conf

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%license LICENSE
%ghost /var/run/setrans
%{_libdir}/libselinux.so.1
%{_prefix}/lib/tmpfiles.d/libselinux.conf

%files utils
%defattr(-,root,root,-)
%{_sbindir}/*
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_mandir}/ru/man5/*
%{_mandir}/ru/man8/*

%files devel
%defattr(-,root,root,-)
%{_libdir}/libselinux.so
%{_libdir}/pkgconfig
%dir %{_includedir}/selinux
%{_includedir}/selinux/*
%{_libdir}/libselinux.a
%{_mandir}/man3/*

%files python
%defattr(-,root,root,-)
%{python2_sitelib}/*

%files python3
%defattr(-,root,root,-)
%{python3_sitelib}/*

%changelog
*   Mon Sep 28 2020 Ruying Chen <v-ruyche@microsoft.com> 2.9-4
-   Provide python3-libselinux for -python3 subpackage
*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 2.9-3
-   Added %%license line automatically
*   Tue Mar 24 2020 Henry Beberman <henry.beberman@microsoft.com> 2.9-2
-   Add -Wno-error=strict-overflow to resolve build break with gcc9
*   Tue Mar 17 2020 Henry Beberman <henry.beberman@microsoft.com> 2.9-1
-   Update to 2.9. Fix Source0 URL. License verified.
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 2.8-3
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Tue Jan 08 2019 Alexey Makhalov <amakhalov@vmware.com> 2.8-2
-   Added BuildRequires python2-devel
*   Fri Aug 10 2018 Srivatsa S. Bhat <srivatsa@csail.mit.edu> 2.8-1
-   Update to version 2.8 to get it to build with gcc 7.3
*   Thu Aug 24 2017 Alexey Makhalov <amakhalov@vmware.com> 2.6-4
-   Fix compilation issue for glibc-2.26
*   Wed May 31 2017 Xiaolin Li <xiaolinl@vmware.com> 2.6-3
-   Include pytho3 packages.
*   Mon May 22 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 2.6-2
-   Include python subpackage.
*   Wed May 03 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 2.6-1
-   Upgraded to version 2.6
*   Tue May 02 2017 Anish Swaminathan <anishs@vmware.com> 2.5-3
-   Remove pcre requires and add requires on pcre-libs
*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 2.5-2
-   GA - Bump release of all rpms
*   Fri Jan 22 2016 Xiaolin Li <xiaolinl@vmware.com> 2.5-1
-   Updated to version 2.5
*   Wed Feb 25 2015 Divya Thaluru <dthaluru@vmware.com> 2.4-1
-   Initial build.  First version
