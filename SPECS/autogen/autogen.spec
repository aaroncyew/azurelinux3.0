Summary:	The Automated Text and Program Generation Tool
Name:		autogen
Version:    5.18.16
Release:    5%{?dist}
License:        GPLv3+
URL:            http://www.gnu.org/software/autogen/
Source0:        ftp://ftp.gnu.org/gnu/autogen/rel%{version}/%{name}-%{version}.tar.xz
Group:		System Environment/Tools
Vendor:         Microsoft Corporation
BuildRequires:	guile-devel
BuildRequires:	gc-devel
BuildRequires:	which

Requires:	guile
Requires:	gc
Requires:	gmp
Requires:   %{name}-libopts
Distribution:   Mariner
%description
AutoGen is a tool designed to simplify the creation and maintenance of programs that contain large amounts of repetitious text. It is especially valuable in programs that have several blocks of text that must be kept synchronized.

%package libopts
Summary:	Automated option processing library.
License:	LGPLv3+
Group:		System Environment/Libraries

%description libopts
Libopts is very powerful command line option parser.

%package libopts-devel
Summary:	Development files for libopts
License:	LGPLv3+
Group:		Development/Libraries
Requires:	%{name}
Requires:	%{name}-libopts

%description libopts-devel
This package contains development files for libopts.

%prep
%setup -q
%build
%configure --disable-dependency-tracking
make %{?_smp_mflags} CFLAGS="%{build_cflags} -Wno-error=format-overflow="
%install
make DESTDIR=%{buildroot} install

%check
make %{?_smp_mflags} check

%post	libopts -p /sbin/ldconfig
%postun	libopts -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license COPYING
%{_bindir}/*
%exclude %{_bindir}/autoopts-config
%{_libdir}/autogen/*.tlib
%{_datadir}/autogen/*
%{_mandir}/man1/*
%exclude %{_mandir}/man1/autoopts-config.1.gz


%files libopts
%{_libdir}/*.so.*

%files libopts-devel
%defattr(-,root,root)
%{_includedir}/autoopts/*.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_bindir}/autoopts-config
%{_datadir}/aclocal/*
%{_mandir}/man1/autoopts-config.1.gz
%{_mandir}/man3/*
%{_libdir}/*.a
%{_libdir}/*.la
%exclude /usr/share/info/

%changelog
* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 5.18.16-5
- Added %%license line automatically

*   Thu Feb 27 2020 Henry Beberman <hebeberm@microsoft.com> 5.18.16-4
-   Add compiler flags for GCC9 compatibility. License verified.
*   Thu Feb 27 2020 Henry Beberman <hebeberm@microsoft.com> 5.18.16-3
-   Exclude /usr/share/info from the RPM
*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 5.18.16-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*       Wed Sep 12 2018 Anish Swaminathan <anishs@vmware.com>  5.18.16-1
-       Upgrade to 5.18.16
*       Mon May 01 2017 Dheeraj Shetty <dheerajs@vmware.com> 5.18.12-2
-       Adding Make Check
*       Tue Apr 18 2017 Dheeraj Shetty <dheerajs@vmware.com> 5.18.12-1
-       Updated version to 5.18.12
*       Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 5.18.7-2
-       GA - Bump release of all rpms
*       Wed Feb 24 2016 Kumar Kaushik <kaushikk@vmware.com> 5.18.7-1
-       Updated version tp 5.16.7.
*       Thu Jan 21 2016 Xiaolin Li <xiaolinl@vmware.com> 5.18.6-1
-       Updated to version 5.18.6
*       Tue Sep 29 2015 Xiaolin Li <xiaolinl@vmware.com> 5.18.5-2
-       Create a seperate libopts package.
*       Thu Jun 18 2015 Divya Thaluru <dthaluru@vmware.com> 5.18.5-1
-       Initial build. First version
