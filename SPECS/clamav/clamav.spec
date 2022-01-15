Summary:        Open source antivirus engine
Name:           clamav
Version:        0.104.2
Release:        1%{?dist}
License:        ASL 2.0 AND BSD AND bzip2-1.0.4 AND GPLv2 AND LGPLv2+ AND MIT AND Public Domain AND UnRar
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Security
URL:            https://www.clamav.net
Source0:        https://github.com/Cisco-Talos/clamav/archive/refs/tags/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gdb
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  python3-pip
BuildRequires:  python3-pytest
BuildRequires:  valgrind

BuildRequires:  bzip2-devel
BuildRequires:  check-devel
BuildRequires:  json-c-devel
BuildRequires:  libcurl-devel
BuildRequires:  libxml2-devel
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  pcre2-devel
BuildRequires:  systemd-devel
BuildRequires:  zlib-devel

Requires:       openssl
Requires:       zlib
Provides:       %{name}-devel = %{version}-%{release}
Provides:       %{name}-lib = %{version}-%{release}

%description
ClamAV® is an open source (GPL) anti-virus engine used in a variety of situations
including email scanning, web scanning, and end point security. It provides a number
of utilities including a flexible and scalable multi-threaded daemon, a command
line scanner and an advanced tool for automatic database updates.

%prep
%autosetup

%build
mkdir -p build
cd build

# Notes:
# - milter must be disable because CBL-Mariner does not provide 'sendmail' packages 
#   which provides the necessary pieces to build 'clamav-milter'
# - systemd should be enabled because default value is off
cmake .. \
    -D CMAKE_INSTALL_PREFIX=/usr \
    -D CMAKE_INSTALL_LIBDIR=lib \
    -D APP_CONFIG_DIRECTORY=/etc/clamav \
    -D DATABASE_DIRECTORY=/var/lib/clamav \
    -D ENABLE_SYSTEMD=ON \
    -D ENABLE_MILTER=OFF \
    -D ENABLE_EXAMPLES=OFF \
    -D ENABLE_TESTS=OFF
cmake --build .
# ctest
# sudo cmake --build . --target install

echo "!!!!! DEBUG ALWAYS FAIL !!!!!"
exit 1
# %configure
# %make_build

%install
%make_install
find %{buildroot} -type f -name "*.la" -delete -print

%check
%make_build check

%ldconfig_scriptlets

%files
%defattr(-,root,root)
%license COPYING COPYING.bzip2 COPYING.file COPYING.getopt COPYING.LGPL COPYING.llvm COPYING.lzma COPYING.pcre COPYING.regex COPYING.unrar COPYING.YARA COPYING.zlib
%{_bindir}/*
%{_sysconfdir}/*.sample
%{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.so.*
%{_libdir}/pkgconfig/*.pc
%{_unitdir}/*
%{_sbindir}/*
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*

%changelog
* Fri Jan 14 2022 Nicolas Guibourge <nicolasg@microsoft.com> - 0.104.2-1
- Upgrade to 0.104.2

* Fri Sep 10 2021 Thomas Crain <thcrain@microsoft.com> - 0.103.2-3
- Remove libtool archive files from final packaging

* Fri Jul 23 2021 Thomas Crain <thcrain@microsoft.com> - 0.103.2-2
- Add provides for devel, lib subpackages
- Use make macros throughout

* Tue Apr 20 2021 Thomas Crain <thcrain@microsoft.com> - 0.103.2-1
- Updating to 0.103.2 to fix CVE-2021-1252, CVE-2021-1404, CVE-2021-1405

* Fri Apr 02 2021 Thomas Crain <thcrain@microsoft.com> - 0.103.0-2
- Merge the following releases from dev to 1.0 spec
- v-ruyche@microsoft.com, 0.101.2-4: Systemd supports merged /usr. Update units file location and macro.

* Tue Oct 27 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 0.103.0-1
- Updating to 0.103.0 to fix: CVE-2019-12625, CVE-2019-15961.

* Mon Oct 19 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 0.101.2-3
- License verified.
- Added %%license macro.
- Switching to using the %%configure macro.
- Extended package's summary and description.

* Wed Oct 02 2019 Mateusz Malisz <mamalisz@microsoft.com> - 0.101.2-2
- Fix vendor and distribution. Add systemd files to the list.

* Thu Jul 25 2019 Chad Zawistowski <chzawist@microsoft.com> - 0.101.2-1
- Initial CBL-Mariner import from Azure.
