Summary:        HA monitor built upon LVS, VRRP and services poller
Name:           keepalived
Version:        2.0.10
Release:        7%{?dist}
License:        GPLv2
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Applications/System
URL:            https://www.keepalived.org/
#Note.          We currently use alternate source location.  Preferred original is here:  https://www.keepalived.org/software/keepalived-%{version}.tar.gz
#Source0:       https://github.com/acassen/keepalived/archive/v%{version}.zip
Source0:        %{name}-%{version}.zip
Source1:        %{name}.service
Patch0:         CVE-2021-44225.patch
BuildRequires:  ipset-devel
BuildRequires:  iptables-devel
BuildRequires:  libmnl-devel
BuildRequires:  libnfnetlink-devel
BuildRequires:  libnl3-devel
BuildRequires:  net-snmp-devel
BuildRequires:  openssl-devel
BuildRequires:  systemd
BuildRequires:  unzip
Requires:       libnl3-devel
Requires:       net-snmp
Requires:       systemd

%description
The main goal of the keepalived project is to add a strong & robust keepalive
facility to the Linux Virtual Server project. This project is written in C with
multilayer TCP/IP stack checks. Keepalived implements a framework based on
three family checks : Layer3, Layer4 & Layer5/7. This framework gives the
daemon the ability to check the state of an LVS server pool. When one of the
servers of the LVS server pool is down, keepalived informs the linux kernel via
a setsockopt call to remove this server entry from the LVS topology. In
addition keepalived implements an independent VRRPv2 stack to handle director
failover. So in short keepalived is a userspace daemon for LVS cluster nodes
healthchecks and LVS directors failover.

%prep
%autosetup -p1

%build
autoreconf -f -i
%configure \
    --with-systemdsystemunitdir=%{_unitdir} \
    --enable-snmp       \
    --enable-snmp-rfc
make %{?_smp_mflags} STRIP=/bin/true

%install
make install DESTDIR=%{buildroot}
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
rm -rf %{buildroot}%{_sysconfdir}/%{name}/samples/*

%check
# A build could silently have LVS support disabled if the kernel includes can't
# be properly found, we need to avoid that.
if ! grep -q "#define _WITH_LVS_ *1" lib/config.h; then
    %{__echo} "ERROR: We do not want keepalived lacking LVS support."
    exit 1
fi

%post
/sbin/ldconfig
%systemd_post keepalived.service

%preun
%systemd_preun keepalived.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart keepalived.service

%files
%defattr(-,root,root)
%license COPYING
%doc %{_docdir}/%{name}/README
%{_sbindir}/%{name}
%{_bindir}/genhash
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%{_datadir}/snmp/mibs/KEEPALIVED-MIB.txt
%{_datadir}/snmp/mibs/VRRP-MIB.txt
%{_datadir}/snmp/mibs/VRRPv3-MIB.txt
%{_mandir}/man1/genhash.1*
%{_mandir}/man5/%{name}.conf.5*
%{_mandir}/man8/%{name}.8*

%changelog
* Sat Dec 04 2021 Mariner Autopatcher <cblmargh@microsoft.com> - 2.0.10-7
- Added patch file(s) CVE-2021-44225.patch

* Thu Apr 15 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0.10-6
- Adding an explicit run-time dependency on 'net-snmp'.
- Bumping up release number to link against newer version of 'net-snmp' libraries.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 2.0.10-5
- Added %%license line automatically

* Thu Apr 30 2020 Nicolas Ontiveros <niontive@microsoft.com> 2.0.10-4
- Rename libnl to libnl3.

* Mon Apr 13 2020 Jon Slobodzian <joslobo@microsoft.com> 2.0.10-3
- Verified license. Removed sha1. Fixed Source0 URL. URL to https. dded note about alternate source location.

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 2.0.10-2
- Initial CBL-Mariner import from Photon (license: Apache2).

* Fri Feb 15 2019 Ashwin H <ashwinh@vmware.com> 2.0.10-1
- Updated to version 2.0.10

* Wed Sep 12 2018 Ankit Jain <ankitja@vmware.com> 2.0.7-1
- Updated to version 2.0.7

* Fri Jun 23 2017 Xiaolin Li <xiaolinl@vmware.com> 1.3.5-2
- Add iptables-devel to BuildRequires

* Thu Apr 06 2017 Dheeraj Shetty <dheerajs@vmware.com> 1.3.5-1
- Initial build.  First version
