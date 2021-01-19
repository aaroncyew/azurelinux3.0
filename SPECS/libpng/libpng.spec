Summary:        contains libraries for reading and writing PNG files.
Name:           libpng
Version:        1.6.37
Release:        2%{?dist}
License:        zlib
# The site does NOT have an HTTPS cert available.
URL:            http://www.libpng.org/
Group:          System Environment/Libraries
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:        https://downloads.sourceforge.net/libpng/%{name}-%{version}.tar.xz

%description
The libpng package contains libraries used by other programs for reading and writing PNG files. The PNG format was designed as a replacement for GIF and, to a lesser extent, TIFF, with many improvements and extensions and lack of patent problems.

%package    devel
Summary:    Header and development files
Requires:   %{name} = %{version}-%{release}

Provides:       pkgconfig(libpng) = %{version}-%{release}
Provides:       pkgconfig(libpng16) = %{version}-%{release}

%description    devel
It contains the libraries and header files to create applications

%prep
%setup -q
%build
%configure
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install

%check
make %{?_smp_mflags} -k check

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%files
%defattr(-,root,root)
%license LICENSE
%{_bindir}/pngfix
%{_bindir}/png-fix-itxt
%{_libdir}/*.so.*
%{_datadir}/man/man5/*

%files devel
%defattr(-,root,root)
%{_bindir}/*-config
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/*.a
%{_libdir}/pkgconfig/*.pc
%{_datadir}/man/man3/*

%changelog
* Tue Jan 19 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.6.37-3
- Moved "Provides" for "pkgconfig(*)" to the correct (-devel) subpackage.
*   Sat May 09 00:20:35 PST 2020 Nick Samson <nisamson@microsoft.com> - 1.6.37-2
-   Added %%license line automatically
*   Fri May 08 2020 Nick Samson <nisamson@microsoft.com> 1.6.37-1
-   Updated to 1.6.37 to resolve CVE-2018-14550 and CVE-2019-7317.
-   Updated Source0 URL. Removed %%sha line.
-   License verified; moniker changed to reflect Fedora standards. 
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 1.6.35-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*       Mon Sep 10 2018 Bo Gan <ganb@vmware.com> 1.6.35-1
-       Update to 1.6.35
*    Tue Apr 11 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.6.29-1
-    Updated to version 1.6.29
*       Thu Feb 23 2017 Divya Thaluru <dthaluru@vmware.com> 1.6.27-1
-       Updated to version 1.6.27
*       Mon Sep 12 2016 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.6.23-2
-       Included the libpng16 pkgconfig
*       Wed Jul 27 2016 Divya Thaluru <dthaluru@vmware.com> 1.6.23-1
-       Initial version
