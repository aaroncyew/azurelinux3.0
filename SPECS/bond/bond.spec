Summary:        Microsoft Bond Library
Name:           bond
Version:        8.0.1
Release:        6%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://github.com/microsoft/bond
Source0:        https://github.com/microsoft/bond/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        gbc-0.11.0.3-x86_64
BuildRequires:  boost-devel
BuildRequires:  clang
BuildRequires:  cmake
BuildRequires:  gmp-devel
BuildRequires:  ncurses-devel
BuildRequires:  rapidjson-devel
BuildRequires:  zlib-devel

ExclusiveArch:  x86_64

%description
Bond is an open-source, cross-platform framework for working with schematized data.
It supports cross-language serialization/deserialization and powerful generic mechanisms
for efficiently manipulating data. Bond is broadly used at Microsoft in high scale services.

%package devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}

%description devel
Development files for %{name}

%prep
%setup -q
chmod u+x %{SOURCE1}

%build
CMAKE_OPTS="\
    -DBOND_ENABLE_GRPC=FALSE \
    -DBOND_FIND_RAPIDJSON=TRUE \
    -DBOND_SKIP_CORE_TESTS=TRUE \
    -DBOND_SKIP_GBC_TESTS=TRUE \
    -DBOND_GBC_PATH=%{SOURCE1} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
"

mkdir -v build
cd build
cmake $CMAKE_OPTS ..
%make_build

%install
cd build
%make_install
chmod 0755 %{buildroot}%{_bindir}/gbc

%files
%license LICENSE
%doc README.md
%{_bindir}/*

%files devel
%{_includedir}/%{name}/*
%{_libdir}/%{name}/*

%changelog
* Wed Sep 27 2023 Nicolas Guibourge <nicolasg@microsoft.com> - 8.0.1-6
- Provide bond 8.0.1 for CBL-Mariner 2.0.

* Tue Nov 30 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 8.0.1-5
- Updating package build steps.

* Tue Oct 27 2020 Joe Schmitt <joschmit@microsoft.com> - 8.0.1-4
- Include all sources regardless of architecture.

* Mon Oct 19 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 8.0.1-3
- License verified.
- Added source URL.
- Added 'Vendor' and 'Distribution' tags.

* Tue May 19 2020 Jonathan Chiu <jochi@microsoft.com> - 8.0.1-2
- Add aarch64 support

* Mon Apr 06 2020 Jonathan Chiu <jochi@microsoft.com> - 8.0.1-1
- Original version for CBL-Mariner.
