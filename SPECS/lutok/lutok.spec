Name:          lutok
Version:       0.4
Release:       16%{?dist}
License:       BSD
Vendor:        Microsoft Corporation
Distribution:  Mariner
URL:           https://github.com/jmmv/lutok
Summary:       Lightweight C++ API library for Lua

Source0:       https://github.com/jmmv/lutok/releases/download/%{name}-%{version}/%{name}-%{version}.tar.gz
Source1:       README

Requires:      lua >= 5.2
BuildRequires: gcc
BuildRequires: libatf-c++-devel >= 0.20
BuildRequires: lua-devel >= 5.2

%define _testsdir %{_libexecdir}/lutok/tests

%description
Lutok provides thin C++ wrappers around the Lua C API to ease the
interaction between C++ and Lua.  These wrappers make intensive use of
RAII to prevent resource leakage, expose C++-friendly data types, report
errors by means of exceptions and ensure that the Lua stack is always
left untouched in the face of errors.  The library also provides a small
subset of miscellaneous utility functions built on top of the wrappers.

Lutok focuses on providing a clean and safe C++ interface; the drawback
is that it is not suitable for performance-critical environments.  In
order to implement error-safe C++ wrappers on top of a Lua C binary
library, Lutok adds several layers or abstraction and error checking
that go against the original spirit of the Lua C API and thus degrade
performance.

%prep
%setup -q

# Put the README file in the top-level directory of the source tree so
# that the %doc call below can pick it up.
cp -p %{SOURCE1} README

%build
%configure --docdir=%{_defaultdocdir}/lutok-doc-%{version} \
           --disable-static \
           --htmldir=%{_defaultdocdir}/lutok-doc-%{version}/html \
           --without-doxygen
make %{?_smp_mflags} testsdir=%{_testsdir}

%check
# In order to enable this, we need to add a BuildRequires on kyua-cli.  The
# problem is that kyua-cli depends on lutok.  Introducing a circular dependency
# for this minor benefit does not seem like the best move.  After all, we can
# always install lutok-tests later and run the tests post-install.
#make check testsdir=%{_testsdir}

%install
make install DESTDIR=%{buildroot} doc_DATA= testsdir=%{_testsdir}
rm %{buildroot}%{_libdir}/liblutok.la

%files
%doc AUTHORS NEWS README
%license COPYING
%{_libdir}/liblutok.so.3
%{_libdir}/liblutok.so.3.0.0

%ldconfig_scriptlets

%package devel
Summary: Libraries and header files for Lutok development
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: lua-devel >= 5.1
Provides: pkgconfig(lutok) = %{version}-%{release}

%description devel
Provides the libraries and header files to develop applications that
use the Lutok C++ API to Lua.

%files devel
%{_includedir}/lutok
%{_libdir}/liblutok.so
%{_libdir}/pkgconfig/lutok.pc

%package doc
Summary: API documentation of the Lutok library and example programs
Requires: %{name} = %{version}-%{release}
BuildArch: noarch

%description doc
Provides HTML documentation describing the API of the Lutok library
and a collection of sample source programs to demonstrate the use
of the library.

%files doc
%{_defaultdocdir}/lutok-doc-%{version}

%package tests
Summary: Run-time tests of the Lutok library
Requires: %{name} = %{version}-%{release}
Requires: %{name}-devel = %{version}-%{release}
Requires: libatf-c++ >= 0.20

%description tests
This package installs the run-time tests for the Lutok library.
Please see the README file in the documentation directory for further
details on how to run the installed tests.

%files tests
%doc README
%{_testsdir}

%changelog
* Mon Sep 28 2020 Joe Schmitt <joschmit@microsoft.com> - 0.4-16
- Initial CBL-Mariner import from Fedora 32 (license: MIT).
- Update URL.
- Update Source0.
- Explicitly provide pkgconfig(lutok).
- Rename README.Fedora to README.
- Add %%license file.
- License verified.

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.4-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.4-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.4-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.4-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.4-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.4-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.4-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.4-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.4-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 0.4-5
- Rebuilt for GCC 5 C++11 ABI change

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Feb 11 2014 Julio Merino <julio@meroh.net> 0.4-2
- Depend on atf-0.20 for libatf-c++ ABI changes.

* Sat Dec 07 2013 Julio Merino <julio@meroh.net> 0.4-1
- Package updated to Lutok 0.4.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 14 2013 Julio Merino <jmmv@google.com> 0.3-1
- Package updated to Lutok 0.3.
- Lutok now supports both Lua 5.1 and 5.2.  The specific version used in this
  release depends on the Fedora branch this package is built for.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 18 2012 Julio Merino <jmmv@google.com> 0.2-2
- Added the lutok-tests package providing the run-time tests of Lutok, readily
  runnable by the end users.

* Wed May 30 2012 Julio Merino <jmmv@google.com> 0.2-1
- Package updated to Lutok 0.2.

* Sun May 06 2012 Julio Merino <jmmv@google.com> 0.1-2
- Made lutok-devel depend on lua-devel (needed for c_gate.hpp).
- Forced lutok and lutok-devel to depend on Lua 5.1; 5.2 is not supported
  by Lutok 0.1.

* Fri Feb 03 2012 Julio Merino <jmmv@google.com> 0.1-1
- Initial release for Fedora.
