Summary:        advanced key-value store
Name:           redis
Version:        6.2.12
Release:        1%{?dist}
License:        BSD
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Applications/Databases
URL:            https://redis.io/
Source0:        https://download.redis.io/releases/%{name}-%{version}.tar.gz
Patch0:         redis-conf.patch
Patch1:         disable_active_defrag_big_keys.patch
Patch2:         disable_defrag_test.patch
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  systemd
BuildRequires:  tcl
BuildRequires:  tcl-devel
BuildRequires:  which
Requires:       systemd
Requires(pre):  %{_sbindir}/groupadd
Requires(pre):  %{_sbindir}/useradd

%description
Redis is an in-memory data structure store, used as database, cache and message broker.

%prep
%autosetup -p1

%build
make %{?_smp_mflags}

%install
install -vdm 755 %{buildroot}
make PREFIX=%{buildroot}%{_prefix} install
install -D -m 0640 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf
mkdir -p %{buildroot}%{_sharedstatedir}/redis
mkdir -p %{buildroot}%{_var}/log
mkdir -p %{buildroot}%{_var}/opt/%{name}/log
ln -sfv %{_var}/opt/%{name}/log %{buildroot}%{_var}/log/%{name}
mkdir -p %{buildroot}/usr/lib/systemd/system
cat << EOF >>  %{buildroot}/usr/lib/systemd/system/redis.service
[Unit]
Description=Redis in-memory key-value database
After=network.target

[Service]
ExecStart=%{_bindir}/redis-server %{_sysconfdir}/redis.conf --daemonize no
ExecStop=%{_bindir}/redis-cli shutdown
User=redis
Group=redis

[Install]
WantedBy=multi-user.target
EOF

%check
make check

%pre
getent group %{name} &> /dev/null || \
groupadd -r %{name} &> /dev/null
getent passwd %{name} &> /dev/null || \
useradd -r -g %{name} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
-c 'Redis Database Server' %{name} &> /dev/null
exit 0

%post
/sbin/ldconfig
%systemd_post  redis.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart redis.service

%files
%defattr(-,root,root)
%license COPYING
%dir %attr(0750, redis, redis) %{_sharedstatedir}/redis
%dir %attr(0750, redis, redis) %{_var}/opt/%{name}/log
%attr(0750, redis, redis) %{_var}/log/%{name}
%{_bindir}/*
%{_libdir}/systemd/*
%config(noreplace) %attr(0640, %{name}, %{name}) %{_sysconfdir}/redis.conf

%changelog
* Thu May 04 2023 Sumedh Sharma <sumsharma@microsoft.com> - 6.2.12-1
- Upgrade to 6.2.12 to fix CVE-2023-28856

* Thu Mar 09 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 6.2.11-1
- Auto-upgrade to 6.2.11 - patch CVE-2022-36021

* Mon Feb 13 2023 Henry Li <lihl@microsoft.com> - 6.2.9-1
- Upgrade to version 6.2.9 to resolve CVE-2022-35977 and CVE-2023-22458

* Wed Oct 26 2022 Aurélien Bombo <abombo@microsoft.com> - 6.2.7-2
- Apply patch for CVE-2022-3647.

* Thu Jul 07 2022 Nick Samson <nisamson@microsoft.com> - 6.2.7-1
- Disabled spuriously failing test (OK according to Redis developer)
- Backport version 6.2.7 to address CVE-2022-24736

* Mon Oct 18 2021 Neha Agarwal <nehaagarwal@microsoft.com> 5.0.14-1
- Update version for CVE-2021-32626, CVE-2021-32627, CVE-2021-32628, CVE-2021-32675, CVE-2021-32687, CVE-2021-32762, CVE-2021-41099

* Fri Apr 09 2021 Suresh Babu Chalamalasetty <schalam@microsoft.com> 5.0.5-7
- Add patch for CVE-2021-3470

* Thu Mar 11 2021 Mateusz Malisz <mamalisz@microsoft.com> 5.0.5-6
- Add nopatch for CVE-2021-21309.

* Wed Mar 03 2021 Andrew Phelps <anphel@microsoft.com> 5.0.5-5
- Add patch to remove an unreliable test. License verified.

* Fri Oct 23 2020 Henry Li <lihl@microsoft.com> 5.0.5-4
- Add patch to resolve CVE-2020-14147

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> 5.0.5-3
- Added %%license line automatically

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 5.0.5-2
- Initial CBL-Mariner import from Photon (license: Apache2).

* Mon Jul 22 2019 Shreyas B. <shreyasb@vmware.com> 5.0.5-1
- Updated to version 5.0.5.

* Tue Sep 11 2018 Keerthana K <keerthanak@vmware.com> 4.0.11-1
- Updated to version 4.0.11.

* Thu Dec 28 2017 Divya Thaluru <dthaluru@vmware.com>  3.2.8-5
- Fixed the log file directory structure

* Mon Sep 18 2017 Alexey Makhalov <amakhalov@vmware.com> 3.2.8-4
- Remove shadow from requires and use explicit tools for post actions

* Wed May 31 2017 Siju Maliakkal <smaliakkal@vmware.com> 3.2.8-3
- Fix DB persistence,log file,grace-ful shutdown issues

* Tue May 16 2017 Siju Maliakkal <smaliakkal@vmware.com> 3.2.8-2
- Added systemd service unit

* Wed Apr 5 2017 Siju Maliakkal <smaliakkal@vmware.com> 3.2.8-1
- Updating to latest version

* Mon Oct 3 2016 Dheeraj Shetty <dheerajs@vmware.com> 3.2.4-1
- initial version
