%define python3_sitelib %{_libdir}/python3.7/site-packages
%define cl_services cloud-config.service cloud-config.target cloud-final.service cloud-init.service cloud-init.target cloud-init-local.service
Summary:        Cloud instance init scripts
Name:           cloud-init
Version:        21.4
Release:        4%{?dist}
License:        GPLv3
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Base
URL:            https://launchpad.net/cloud-init
Source0:        https://launchpad.net/cloud-init/trunk/%{version}/+download/%{name}-%{version}.tar.gz
Source1:        dscheck_VMwareGuestInfo
Source2:        10-azure-kvp.cfg
Patch0:         cloud-init-azureds.patch
Patch1:         ds-identify.patch
Patch2:         ds-vmware-mariner.patch
Patch3:         cloud-cfg.patch
# Add Mariner distro support to cloud-init
Patch4:         mariner-21.4.patch
# backport patch https://github.com/canonical/cloud-init/commit/0988fb89be06aeb08083ce609f755509d08fa459.patch to 21.4
Patch5:         azureds-set-ovf_is_accesible.patch
Patch6:         CVE-2023-1786.patch
Patch7:         CVE-2022-2084.patch

BuildRequires:  automake
BuildRequires:  dbus
BuildRequires:  iproute
BuildRequires:  python3
BuildRequires:  python3-PyYAML
BuildRequires:  python3-certifi
BuildRequires:  python3-chardet
BuildRequires:  python3-configobj
BuildRequires:  python3-idna
BuildRequires:  python3-ipaddr
BuildRequires:  python3-jinja2
BuildRequires:  python3-libs
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
BuildRequires:  python3-six
BuildRequires:  python3-xml
BuildRequires:  systemd
BuildRequires:  systemd-devel
Requires:       dhcp-client
Requires:       iproute
Requires:       net-tools
Requires:       python3
Requires:       python3-PyYAML
Requires:       python3-configobj
Requires:       python3-jinja2
Requires:       python3-jsonpatch
Requires:       python3-jsonschema
Requires:       python3-libs
Requires:       python3-markupsafe
Requires:       python3-netifaces
Requires:       python3-oauthlib
Requires:       python3-prettytable
Requires:       python3-requests
Requires:       python3-setuptools
Requires:       python3-six
Requires:       python3-xml
Requires:       systemd
BuildArch:      noarch
%if %{with_check}
BuildRequires:  python3-configobj
BuildRequires:  python3-jsonpatch
BuildRequires:  python3-pip
BuildRequires:  python3-pytest
BuildRequires:  shadow-utils
%endif

%description
Cloud-init is a set of init scripts for cloud instances.  Cloud instances
need special scripts to run during initialization to retrieve and install
ssh keys and to let the user run various scripts.

%package azure-kvp
Summary:        Cloud-init configuration for Hyper-V telemetry
Requires:       %{name} = %{version}-%{release}

%description    azure-kvp
Cloud-init configuration for Hyper-V telemetry

%prep
%autosetup -p1 -n %{name}-%{version}

find systemd -name "cloud*.service*" | xargs sed -i s/StandardOutput=journal+console/StandardOutput=journal/g

%build
python3 setup.py build

%install
python3 setup.py install -O1 --skip-build --root=%{buildroot} --init-system=systemd

python3 tools/render-cloudcfg --variant mariner > %{buildroot}/%{_sysconfdir}/cloud/cloud.cfg

%if "%{_arch}" == "aarch64"
# OpenStack DS in aarch64 adds a boot time of ~10 seconds by searching
# for DS from a remote location, let's remove it.
sed -i -e "0,/'OpenStack', / s/'OpenStack', //" %{buildroot}/%{_sysconfdir}/cloud/cloud.cfg
%endif

mkdir -p %{buildroot}%{_sharedstatedir}/cloud
mkdir -p %{buildroot}/%{_sysconfdir}/cloud/cloud.cfg.d

install -m 755 %{SOURCE1} %{buildroot}/%{_bindir}
install -m 644 %{SOURCE2} %{buildroot}/%{_sysconfdir}/cloud/cloud.cfg.d/

%check
touch vd ud

mkdir -p %{_datadir}/ca-certificates/
crt_file='%{_datadir}/ca-certificates/cloud-init-ca-certs.crt'
echo -e 'CERT1\nLINE2\nLINE3\nCERT2\nLINE2\nLINE3' > "${crt_file}"

conf_file='%{_sysconfdir}/ca-certificates.conf'
echo -e 'line1\nline2\nline3\ncloud-init-ca-certs.crt\n' > "${conf_file}"

%define test_pkgs pytest-metadata unittest2 mock attrs iniconfig httpretty netifaces

pip3 install --upgrade %{test_pkgs}

# temporarily disable failing tests, common error:
# RuntimeError: duplicate mac found! both 'calixxx' and 'calixxx' have mac 'ee:ee:ee:ee:ee:ee'
rm cloudinit/sources/tests/test_oracle.py
rm tests/unittests/test_net_freebsd.py

make check %{?_smp_mflags}

%clean
rm -rf %{buildroot}


%post
%systemd_post %{cl_services}

%preun
%systemd_preun %{cl_services}

%postun
%systemd_postun %{cl_services}

%files
%{_bindir}/*
%license LICENSE
%{python3_sitelib}/*
%{_docdir}/cloud-init/*
%{_libdir}/cloud-init/*
%dir %{_sharedstatedir}/cloud
%dir %{_sysconfdir}/cloud/templates
%doc %{_sysconfdir}/cloud/cloud.cfg.d/README
%{_sysconfdir}/dhcp/dhclient-exit-hooks.d/hook-dhclient
%{_sysconfdir}/NetworkManager/dispatcher.d/hook-network-manager
%config(noreplace) %{_sysconfdir}/cloud/templates/*
%config(noreplace) %{_sysconfdir}/cloud/cloud.cfg
%config(noreplace) %{_sysconfdir}/cloud/cloud.cfg.d/05_logging.cfg
%{_unitdir}/*
%{_systemdgeneratordir}/cloud-init-generator
%{_udevrulesdir}/66-azure-ephemeral.rules
%{_sysconfdir}/systemd/system/sshd-keygen@.service.d/disable-sshd-keygen-if-cloud-init-active.conf
%{_datadir}/bash-completion/completions/cloud-init

%files azure-kvp
%config(noreplace) %{_sysconfdir}/cloud/cloud.cfg.d/10-azure-kvp.cfg

%changelog
* Mon Jul 03 2023 Minghe Ren <mingheren@microsoft.com> - 21.4-4
- Add patch for CVE-2022-2084 and modify CVE-2023-1786.patch

* Thu Jun 15 2023 Minghe Ren <mingheren@microsoft.com> - 21.4-3
- Add patch for CVE-2023-1786

* Tue Mar 22 2022 Anirudh Gopal <angop@microsoft.com> - 21.4-2
- Backport cloud-init ovf_is_accessible DataSourceAzure.py fix to 21.4

* Wed Mar 16 2022 Henry Beberman <henry.beberman@microsoft.com> - 21.4-1
- Update to version 21.4
- Remove several upstreamed patches already present in source
- Add netplan support into the Mariner distro config

* Tue Feb 22 2022 Henry Beberman <henry.beberman@microsoft.com> - 21.3-4
- Add patches from upstream to resolve a hang when reinitializing preprovisioned VMs.

* Mon Oct 18 2021 Henry Beberman <henry.beberman@microsoft.com> - 21.3-3
- Add azure-kvp subpackage.

* Wed Sep 15 2021 Jiri Appl <jiria@microsoft.com> - 21.3-2
- Port from Photon to Mariner
- Fix dependencies
- Add Mariner patch

* Wed Aug 25 2021 Shreenidhi Shedi <sshedi@vmware.com> 21.3-1
- Upgrade to version 21.3

* Fri Aug 13 2021 Shreenidhi Shedi <sshedi@vmware.com> 21.2-5
- Fix a silly mistake in sed command

* Tue Aug 03 2021 Shreenidhi Shedi <sshedi@vmware.com> 21.2-4
- Fix hostname handling
- Remove OpenStack from aarch64 DS list

* Wed Jul 21 2021 Shreenidhi Shedi <sshedi@vmware.com> 21.2-2
- Support ntp configs

* Mon Jun 21 2021 Shreenidhi Shedi <sshedi@vmware.com> 21.2-1
- Upgrade to version 21.2
- Refactored ds-guestinfo-photon.patch to generate netcfg v2
- Added fallback-netcfg.patch to handle net configs when no DS present

* Tue Apr 20 2021 Shreenidhi Shedi <sshedi@vmware.com> 21.1-2
- Further fixes to network config handler

* Sun Feb 28 2021 Shreenidhi Shedi <sshedi@vmware.com> 21.1-1
- Upgrade to version 21.1

* Wed Jan 20 2021 Shreenidhi Shedi <sshedi@vmware.com> 20.4.1-1
- Upgrade to version 20.4.1

* Thu Dec 10 2020 Shreenidhi Shedi <sshedi@vmware.com> 20.4-1
- Upgrade to version 20.4

* Sun Nov 22 2020 Shreenidhi Shedi <sshedi@vmware.com> 20.3-4
- Added support for network config v1 & v2

* Fri Nov 06 2020 Tapas Kundu <tkundu@vmware.com> 20.3-3
- Updated using python 3.9 lib

* Mon Oct 12 2020 Shreenidhi Shedi <sshedi@vmware.com> 20.3-2
- Fixed subp import in photon.py
- Fixed creating `[Route]` entries while creating network files

* Thu Sep 24 2020 Shreenidhi Shedi <sshedi@vmware.com> 20.3-1
- Upgrade cloud-init to 20.3
- Updated DataSourceVMwareGuestInfo (till commit abc387c7)

* Tue Sep 08 2020 Shreenidhi Shedi <sshedi@vmware.com> 20.2-5
- Further fixes to 'passwd' field
- Fixed an issue with setting fqdn as hostname

* Thu Jul 30 2020 Tapas Kundu <tkundu@vmware.com> 20.2-4
- Updated using python 3.8 lib

* Thu Jul 30 2020 Shreenidhi Shedi <sshedi@vmware.com> 20.2-3
- Bring back 'passwd' field in create_user

* Mon Jul 27 2020 Shreenidhi Shedi <sshedi@vmware.com> 20.2-2
- 1. add support to configure DHCP4 UseDomains= in Networking Config Version 2
- 2. add support for DEFAULT-RUN-POST-CUSTOM-SCRIPT
- 3. fix distro patch for multiple NICs

* Fri Jul 10 2020 Shreenidhi Shedi <sshedi@vmware.com> 20.2-1
- Upgrade version to 20.2
- Support for Networking Config Version 2

* Fri Mar 27 2020 Shreenidhi Shedi <sshedi@vmware.com> 19.1-7
- Fixed make check
- Enable all harmless options
- Generate cloud.cfg using render-cloudcfg script

* Fri Mar 27 2020 Shreenidhi Shedi <sshedi@vmware.com> 19.1-6
- Updated ds-guestinfo-photon.patch
- Fixed dhcp issue in photon-distro.patch
- Updated DataSourceVMwareGuestInfo.patch (till commit bf996d9 from mainline)

* Fri Feb 14 2020 Shreenidhi Shedi <sshedi@vmware.com> 19.1-5
- Fix for CVE-2020-8631

* Tue Feb 11 2020 Shreenidhi Shedi <sshedi@vmware.com> 19.1-4
- Fix for CVE-2020-8632

* Fri Dec 13 2019 Shreenidhi Shedi <sshedi@vmware.com> 19.1-3
- Enabled power-state-change in cloud-photon.cfg file
- Updated DataSourceVMwareGuestInfo.patch (till commit 9e69060 from mainline)
- Updated dscheck_VMwareGuestInfo and ds-guestinfo-photon.patch

* Thu Oct 17 2019 Keerthana K <keerthanak@vmware.com> 19.1-2
- Fix to deactivate custom script by default in DatasourceOVF.
- add kubeadm module

* Thu Sep 19 2019 Keerthana K <keerthanak@vmware.com> 19.1-1
- Update to 19.1
- Patches for enable custom script feature.

* Thu Sep 05 2019 Keerthana K <keerthanak@vmware.com> 18.3-6
- Fix socket.getfqdn() in DataSourceVMwareGuestInfo
- Return False when no data is found in get_data() of DataSourceVMwareGuestInfo.
- Disable manage_etc_hosts by default as cloud-init tries to write its default template /etc/hosts file if enabled.

* Mon Aug 12 2019 Keerthana K <keerthanak@vmware.com> 18.3-5
- Downgrade to 18.3 to fix azure dhcp lease issue.

* Tue Jul 23 2019 Keerthana K <keerthanak@vmware.com> 19.1-2
- support for additional features in VMGuestInfo Datasource.

* Tue Jun 25 2019 Keerthana K <keerthanak@vmware.com> 19.1-1
- Upgrade to version 19.1 and fix cloud-init GOS logic.

* Thu Jun 13 2019 Keerthana K <keerthanak@vmware.com> 18.3-4
- Fix to delete the contents of /etc/systemd/network dir at the beginning
- of write_network instead of looping through each NIC and delete the contents
- before writing a custom network file.

* Tue May 28 2019 Keerthana K <keerthanak@vmware.com> 18.3-3
- Delete the contents of network directory before adding the custom network files.

* Tue Dec 04 2018 Ajay Kaher <akaher@vmware.com> 18.3-2
- Fix auto startup at boot time

* Wed Oct 24 2018 Ajay Kaher <akaher@vmware.com> 18.3-1
- Upgraded version to 18.3

* Sun Oct 07 2018 Tapas Kundu <tkundu@vmware.com> 0.7.9-15
- Updated using python 3.7 lib

* Wed Feb 28 2018 Anish Swaminathan <anishs@vmware.com> 0.7.9-14
- Add support for systemd constructs for azure DS

* Mon Oct 16 2017 Vinay Kulkarni <kulakrniv@vmware.com> 0.7.9-13
- Support configuration of systemd resolved.conf

* Wed Sep 20 2017 Alexey Makhalov <amakhalov@vmware.com> 0.7.9-12
- Requires net-tools or toybox

* Wed Sep 20 2017 Anish Swaminathan <anishs@vmware.com> 0.7.9-11
- Fix the interface id returned from vmxguestinfo

* Tue Aug 22 2017 Chang Lee <changlee@vmware.com> 0.7.9-10
- Fixed %check

* Wed Jul 19 2017 Divya Thaluru <dthaluru@vmware.com> 0.7.9-9
- Enabled openstack provider

* Wed Jun 28 2017 Anish Swaminathan <anishs@vmware.com> 0.7.9-8
- Restart network service in bring_up_interfaces

* Thu Jun 22 2017 Xiaolin Li <xiaolinl@vmware.com> 0.7.9-7
- Add python3-setuptools and python3-xml to requires.

* Wed Jun 07 2017 Xiaolin Li <xiaolinl@vmware.com> 0.7.9-6
- Add python3-setuptools and python3-xml to python3 sub package Buildrequires.

* Mon Jun 5 2017 Julian Vassev <jvassev@vmware.com> 0.7.9-5
- Enable OVF datasource by default

* Mon May 22 2017 Kumar Kaushik <kaushikk@vmware.com> 0.7.9-4
- Making cloud-init to use python3.

* Mon May 15 2017 Anish Swaminathan <anishs@vmware.com> 0.7.9-3
- Disable networking config by cloud-init

* Thu May 04 2017 Anish Swaminathan <anishs@vmware.com> 0.7.9-2
- Support userdata in vmx guestinfo

* Thu Apr 27 2017 Anish Swaminathan <anishs@vmware.com> 0.7.9-1
- Upgraded to version 0.7.9
- Enabled VmxGuestinfo datasource

* Thu Apr 27 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 0.7.6-17
- Fix Arch

* Wed Mar 29 2017 Kumar Kaushik <kaushikk@vmware.com>  0.7.6-16
- Adding support for disk partition and resize fs

* Thu Dec 15 2016 Dheeraj Shetty <dheerajs@vmware.com>  0.7.6-15
- Adding template file and python-jinja2 dependency to update hosts

* Tue Dec 13 2016 Dheeraj Shetty <dheerajs@vmware.com>  0.7.6-14
- Fixed restarting of sshd daemon

* Tue Nov 22 2016 Kumar Kaushik <kaushikk@vmware.com>  0.7.6-13
- Adding flag for vmware customization in config.

* Tue Nov 1 2016 Divya Thaluru <dthaluru@vmware.com>  0.7.6-12
- Fixed logic to not restart services after upgrade

* Mon Oct 24 2016 Divya Thaluru <dthaluru@vmware.com>  0.7.6-11
- Enabled ssh module in cloud-init

* Thu May 26 2016 Divya Thaluru <dthaluru@vmware.com>  0.7.6-10
- Fixed logic to restart the active services after upgrade

* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 0.7.6-9
- GA - Bump release of all rpms

* Tue May 3 2016 Divya Thaluru <dthaluru@vmware.com>  0.7.6-8
- Clean up post, preun, postun sections in spec file.

* Thu Dec 10 2015 Xiaolin Li <xiaolinl@vmware.com>
- Add systemd to Requires and BuildRequires.

* Thu Sep 17 2015 Kumar Kaushik <kaushikk@vmware.com>
- Removing netstat and replacing with ip route.

* Tue Aug 11 2015 Kumar Kaushik <kaushikk@vmware.com>
- VCA initial password issue fix.

* Thu Jun 25 2015 Kumar Kaushik <kaushikk@vmware.com>
- Removing systemd-service.patch. No longer needed.

* Thu Jun 18 2015 Vinay Kulkarni <kulkarniv@vmware.com>
- Add patch to enable logging to /var/log/cloud-init.log

* Mon May 18 2015 Touseef Liaqat <tliaqat@vmware.com>
- Update according to UsrMove.

* Wed Mar 04 2015 Mahmoud Bassiouny <mbassiouny@vmware.com>
- Initial packaging for Photon
