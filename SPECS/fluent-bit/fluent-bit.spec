%define _build_id_links none

Name:           fluent-bit
Summary:        Fast and Lightweight Log processor and forwarder for Linux, BSD and OSX
Version:        1.8.12
Release:        1%{?dist}
License:        ASL 2.0
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://fluentbit.io
#Source0:       https://github.com/fluent/%{name}/archive/v%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  pkgconfig
BuildRequires:  make
BuildRequires:  cmake
BuildRequires:  systemd-rpm-macros
BuildRequires:  systemd-devel
BuildRequires:  gcc-c++
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  doxygen
BuildRequires:  graphviz
BuildRequires:  libpq-devel
BuildRequires:  zlib-devel
BuildRequires:  gnutls-devel
BuildRequires:  openssl-devel
BuildRequires:  cyrus-sasl-devel

%description
Fluent Bit is a fast Log Processor and Forwarder for Linux, Embedded Linux, MacOS and BSD 
family operating systems. It's part of the Fluentd Ecosystem and a CNCF sub-project.

%package devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}

%description devel
Development files for %{name}

%prep
%setup -q

%build
	
%cmake\
    -DCMAKE_BUILD_TYPE=RelWithDebInfo\
    -DFLB_EXAMPLES=Off\
    -DFLB_OUT_SLACK=Off\
    -DFLB_IN_SYSTEMD=On\
    -DFLB_OUT_TD=Off\
    -DFLB_OUT_ES=Off\
    -DFLB_SHARED_LIB=On\
    -DFLB_TESTS_RUNTIME=On\
    -DFLB_TESTS_INTERNAL=Off\
    -DFLB_RELEASE=On\
    -DFLB_DEBUG=Off\
    -DFLB_TLS=On
 
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%exclude /usr/src/debug
/lib/systemd/system/fluent-bit.service
%{_bindir}/*
/usr/etc/fluent-bit/*

%files devel
%{_includedir}/*
/usr/lib/fluent-bit/*.so

%changelog
* Tue Feb 01 2022 Cameron Baird <cameronbaird@microsoft.com> 1.8.12-1
- Update to version 1.8.12

* Mon May 24 2021 Suresh Babu Chalamalasetty <schalam@microsoft.com> 1.5.2-1
- Update to version 1.5.2

* Mon Oct 19 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 1.4.1-2
- License verified.
- Fixed source URL.
- Added 'Vendor' and 'Distribution' tags.
* Mon Mar 30 2020 Jonathan Chiu <jochi@microsoft.com> 1.4.1-1
- Original version for CBL-Mariner.

