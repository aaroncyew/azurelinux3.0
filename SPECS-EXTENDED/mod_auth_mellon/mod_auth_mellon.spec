%bcond_with user_guide
Summary:        A SAML 2.0 authentication module for the Apache Httpd Server
Name:           mod_auth_mellon
Version:        0.16.0
Release:        4%{?dist}
License:        GPLv2+
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://github.com/latchset/mod_auth_mellon
Source0:        https://github.com/latchset/mod_auth_mellon/releases/download/v0_16_0/mod_auth_mellon-0.16.0.tar.gz
Source1:        auth_mellon.conf
Source2:        10-auth_mellon.conf
Source3:        mod_auth_mellon.conf
Source4:        mellon_create_metadata.sh
Source5:        README.redhat.rst
Patch0:         CVE-2021-3639.patch
BuildRequires:  curl-devel
BuildRequires:  gcc
BuildRequires:  glib2-devel
BuildRequires:  httpd-devel
BuildRequires:  lasso-devel >= 2.5.1-13
BuildRequires:  openssl-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  xmlsec1-devel
Requires:       httpd-mmn
Requires:       lasso >= 2.5.1-13
%if %{with user_guide}
BuildRequires:  rubygem-asciidoctor
%endif

%description
The mod_auth_mellon module is an authentication service that implements the
SAML 2.0 federation protocol. It grants access based on the attributes
received in assertions generated by a IdP server.

%prep
%autosetup -p1

%build
export APXS=%{_httpd_apxs}
%configure --enable-diagnostics
make clean
make %{?_smp_mflags}
cp .libs/%{name}.so %{name}-diagnostics.so

%configure
make clean
make %{?_smp_mflags}

%if %{with user_guide}
pushd doc/user_guide
asciidoctor -a data-uri mellon_user_guide.adoc
popd
%endif

%install
# install module
mkdir -p %{buildroot}%{_httpd_moddir}
install -m 755 .libs/%{name}.so %{buildroot}%{_httpd_moddir}
install -m 755 %{name}-diagnostics.so %{buildroot}%{_httpd_moddir}

# install module configuration
mkdir -p %{buildroot}%{_httpd_confdir}
install -m 644 %{SOURCE1} %{buildroot}%{_httpd_confdir}
mkdir -p %{buildroot}%{_httpd_modconfdir}
install -m 644 %{SOURCE2} %{buildroot}%{_httpd_modconfdir}

mkdir -p %{buildroot}%{_tmpfilesdir}
install -m 644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}
mkdir -p %{buildroot}/run/%{name}

# install script to generate metadata
mkdir -p %{buildroot}/%{_libexecdir}/%{name}
install -m 755 %{SOURCE4} %{buildroot}/%{_libexecdir}/%{name}

#install documentation
mkdir -p %{buildroot}/%{_pkgdocdir}

# install Red Hat README
install %{SOURCE5} %{buildroot}/%{_pkgdocdir}

%if %{with user_guide}
# install user guide
cp -r doc/user_guide %{buildroot}/%{_pkgdocdir}
%endif

%package diagnostics
Summary:        Build of mod_auth_mellon with diagnostic logging
Requires:       %{name} = %{version}-%{release}

%description diagnostics
Build of mod_auth_mellon with diagnostic logging. See README.redhat.rst
in the doc directory for instructions on using the diagnostics build.

%files diagnostics
%{_httpd_moddir}/%{name}-diagnostics.so

%files
%license COPYING
%doc README.md NEWS ECP.rst
%doc %{_pkgdocdir}/README.redhat.rst
%if %{with user_guide}
%doc %{_pkgdocdir}/user_guide
%endif
%config(noreplace) %{_httpd_modconfdir}/10-auth_mellon.conf
%config(noreplace) %{_httpd_confdir}/auth_mellon.conf
%{_httpd_moddir}/mod_auth_mellon.so
%{_tmpfilesdir}/mod_auth_mellon.conf
%{_libexecdir}/%{name}
%dir /run/%{name}/

%changelog
* Wed Aug 30 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 0.16.0-4
- Add patch for CVE-2021-3639

* Tue Mar 15 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 0.16.0-3
- Adding missing BR on 'systemd-rpm-macros'.
- License verified.

* Wed Sep 01 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 0.16.0-2
- Initial CBL-Mariner import from Fedora 32 (license: MIT).
- Making user guide build conditional.

* Mon Feb  3 2020 Jakub Hrozek <jhrozek@redhat.com> - 0.16.0-1
- New upstream version 0.16.0

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.15.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Tue Nov 19 2019 Jakub Hrozek <jhrozek@redhat.com> - 0.15.0-1
- New upstream version 0.15.0
- Resolves: rhbz#1725742 - CVE-2019-13038 mod_auth_mellon: an Open Redirect
                           via the login?ReturnTo= substring which could
                           facilitate information theft [fedora-all]

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.14.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Mar 22 2019 Jakub Hrozek <jhrozek@redhat.com> - 0.14.2-1
- Upgrade to 0.14.2
- Related: rhbz#1691771 - CVE-2019-3877 mod_auth_mellon: open redirect in
                          logout url when using URLs with backslashes
- Related: rhbz#1691136 - CVE-2019-3878 mod_auth_mellon: authentication
                          bypass in ECP flow

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.14.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.14.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed May  2 2018 John Dennis <jdennis@redhat.com> - 0.14.0-3
- update lasso version dependency

* Tue May  1 2018 John Dennis <jdennis@redhat.com> - 0.14.0-2
- clean diagnostics build prior to normal build

* Thu Apr 19 2018 John Dennis <jdennis@redhat.com> - 0.14.0-1
- Upgrade to new upstream release
- Add README.redhat.rst doc explaining packaging of this module.

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.13.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sun Oct  1 2017 John Dennis <jdennis@redhat.com> - 0.13.1-1
- upgrade to new upstream release

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.12.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.12.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.12.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 17 2017 John Dennis <jdennis@redhat.com> - 0.12.0-4
- Resolves: bug #1414019 Incorrect PAOS Content-Type header

* Mon Jan  9 2017 John Dennis <jdennis@redhat.com> - 0.12.0-3
- bump release for rebuild

* Tue May  3 2016 John Dennis <jdennis@redhat.com> - 0.12.0-2
- Resolves: bug #1332729, mellon conflicts with mod_auth_openidc
- am_check_uid() should be no-op if mellon not enabled

* Wed Mar  9 2016 John Dennis <jdennis@redhat.com> - 0.12.0-1
- Update to new upstream 0.12.0
- [CVE-2016-2145] Fix DOS attack (Apache worker process crash) due to
  incorrect error handling when reading POST data from client.
- [CVE-2016-2146] Fix DOS attack (Apache worker process crash /
  resource exhaustion) due to missing size checks when reading
  POST data.
In addition this release contains the following new features and fixes:
- Add MellonRedirectDomains option to limit the sites that
  mod_auth_mellon can redirect to. This option is enabled by default.
- Add support for ECP service options in PAOS requests.
- Fix AssertionConsumerService lookup for PAOS requests.

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Dec 23 2015 John Dennis <jdennis@redhat.com> - 0.11.0-3
- Fix the following warning that appears in the Apache log
  lasso-CRITICAL **: lasso_provider_get_metadata_list_for_role: assertion '_lasso_provider_get_role_index(role)' failed

* Fri Sep 18 2015 John Dennis <jdennis@redhat.com> - 0.11.0-2
- Add lasso 2.5.0 version dependency

* Fri Sep 18 2015 John Dennis <jdennis@redhat.com> - 0.11.0-1
- Upgrade to upstream 0.11.0 release.
- Includes ECP support, see NEWS for all changes.
- Update mellon_create_metadata.sh to match internally generated metadata,
  includes AssertionConsumerService for postResponse, artifactResponse &
  paosResponse.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jan  7 2015 Simo Sorce <simo@redhat.com> 0.10.0-1
- New upstream release

* Tue Sep  2 2014 Simo Sorce <simo@redhat.com> 0.9.1-1
- New upstream release

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jun 24 2014 Simo Sorce <simo@redhat.com> 0.8.0-1
- New upstream realease version 0.8.0
- Upstream moved to github
- Drops patches as they have been all included upstream

* Fri Jun 20 2014 Simo Sorce <simo@redhat.com> 0.7.0-3
- Backport of useful patches from upstream
  - Better handling of IDP reported errors
  - Better handling of session data storage size

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Dec 10 2013 Simo Sorce <simo@redhat.com> 0.7.0-1
- Fix ownership of /run files

* Wed Nov 27 2013 Simo Sorce <simo@redhat.com> 0.7.0-0
- Initial Fedora release based on version 0.7.0
- Based on an old spec file by Jean-Marc Liger <jmliger@siris.sorbonne.fr>
