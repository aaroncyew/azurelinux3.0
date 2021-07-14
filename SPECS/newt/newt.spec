Summary:	  A library for text mode user interfaces
Name:		  newt
Version:	  0.52.21
Release:      2%{?dist}
License:	  LGPLv2
URL:		  https://pagure.io/newt
Group:		  Development/Languages
Source0:      https://pagure.io/releases/%{name}/%{name}-%{version}.tar.gz
Vendor:       Microsoft Corporation
Distribution: Mariner

Requires: slang
BuildRequires: slang-devel
BuildRequires: popt-devel
BuildRequires: python3-devel

%description

Newt is a programming library for color text mode, widget based user
interfaces.  Newt can be used to add stacked windows, entry widgets,
checkboxes, radio buttons, labels, plain text fields, scrollbars,
etc., to text mode user interfaces.  This package also contains the
shared library needed by programs built with newt, as well as a
/usr/bin/dialog replacement called whiptail.  Newt is based on the
slang library.

%package	devel
Summary:	Header and development files for newt
Requires:	%{name} = %{version}

%description	devel
It contains the libraries and header files to create applications

%package -n python3-newt
Summary:  Python 3 bindings for newt
Provides: %{name}-python3 = %{version}-%{release}
Provides: %{name}-python3%{?_isa} = %{version}-%{release}
Provides: snack = %{version}-%{release}
Requires: %{name}%{?_isa} = %{version}-%{release}

%description -n python3-newt
The python3-newt package contains the Python 3 bindings for the newt library
providing a python API for creating text mode interfaces.


%prep
%setup -q

%build
./configure --prefix=/usr \
            --with-gpm-support \
            --disable-static

make
%install
make DESTDIR=%{buildroot} install
find %{buildroot} -name '*.la' -delete
find %{buildroot} -name '*.a' -delete

%check
make %{?_smp_mflags} test

%files
%defattr(-,root,root)
%license COPYING
%{_libdir}/libnewt.so.0*
%{_bindir}/*
%{_datadir}/*


%files devel
%{_includedir}/*
%{_libdir}/libnewt.so
%{_libdir}/pkgconfig/*.pc

%files -n python3-newt
%doc peanuts.py popcorn.py
%{python3_sitearch}/*.so
%{python3_sitearch}/*.py*
%{python3_sitearch}/__pycache__/*.py*

%changelog
* Tue Jul 13 2021 Muhammad Falak R Wani <mwani@microsoft.com> 0.52.21-2
- Extend using Fedora 32 spec (license: MIT)
- Enable python3-newt

* Wed Jun 17 2020 Joe Schmitt <joschmit@microsoft.com> 0.52.21-1
- Update to version 0.52.21.
- Update URL.
- Update Source0.
- Remove sha1 macro.
- License verified.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 0.52.20-3
- Added %%license line automatically

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 0.52.20-2
- Initial CBL-Mariner import from Photon (license: Apache2).

* Sat Apr 15 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 0.52.20-1
- Update to 0.52.20

* Mon Oct 04 2016 ChangLee <changLee@vmware.com> 0.52.18-3
- Modified %check

* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 0.52.18-2
- GA - Bump release of all rpms

* Tue Oct 27 2015 Mahmoud Bassiouny <mbassiouny@vmware.com>
- Initial build.	First version
