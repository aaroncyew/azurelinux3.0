Summary:        An URL retrieval utility and library
Name:           curl
Version:        7.84.0
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/NetworkingLibraries
URL:            https://curl.haxx.se
Source0:        https://curl.haxx.se/download/%{name}-%{version}.tar.gz
BuildRequires:  krb5-devel
BuildRequires:  libssh2-devel
BuildRequires:  openssl-devel
Requires:       curl-libs = %{version}-%{release}
Requires:       krb5
Requires:       libssh2
Requires:       openssl

%description
The cURL package contains an utility and a library used for
transferring files with URL syntax to any of the following
protocols: FTP, FTPS, HTTP, HTTPS, SCP, SFTP, TFTP, TELNET,
DICT, LDAP, LDAPS and FILE. Its ability to both download and
upload files can be incorporated into other programs to support
functions like streaming media.

%package devel
Summary:        Libraries and header files for curl
Requires:       %{name} = %{version}-%{release}
Provides:       libcurl-devel = %{version}-%{release}

%description devel
Static libraries and header files for the support library for curl

%package libs
Summary:        Libraries for curl
Group:          System Environment/Libraries
Provides:   libcurl = %{version}-%{release}

%description libs
This package contains minimal set of shared curl libraries.

%prep
%autosetup -p1

%build
# CVE-2021-22922 and CVE-2021-22923 are vulnerabilities when curl's metalink
# feature. We do not build with "--with-libmetalink" option and are therefore
# not affected by these CVEs, but I am placing this comment here as a reminder
# to leave metalink disabled.
%configure \
    CFLAGS="%{optflags}" \
    CXXFLAGS="%{optflags}" \
    --disable-static \
    --enable-threaded-resolver \
    --with-ssl \
    --with-gssapi \
    --with-libssh2 \
    --with-ca-bundle=%{_sysconfdir}/pki/tls/certs/ca-bundle.trust.crt \
    --with-ca-path=%{_sysconfdir}/ssl/certs
make %{?_smp_mflags}

%install
[ %{buildroot} != "/"] && rm -rf %{buildroot}/*
make DESTDIR=%{buildroot} install
install -v -d -m755 %{buildroot}/%{_docdir}/%{name}-%{version}
find %{buildroot} -type f -name "*.la" -delete -print
%{_fixperms} %{buildroot}/*

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license COPYING
%{_bindir}/*
%{_mandir}/man1/*

%files devel
%defattr(-,root,root)
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%{_mandir}/man3/*
%{_datarootdir}/aclocal/libcurl.m4
%{_docdir}/%{name}-%{version}

%files libs
%{_libdir}/libcurl.so.*

%changelog
* Tue Jul 19 2022 Henry Li <lihl@microsoft.com> - 7.84.0-1
- Upgrade to version 7.84.0 to resolve CVE-2022-32207

* Mon Jun 20 2022 Henry Beberman <henry.beberman@microsoft.com> - 7.83.1-1
- Update to version 7.83.1
- Address CVE-2022-27779, CVE-2022-27780, CVE-2022-27781
- Address CVE-2022-30115, CVE-2022-27782, CVE-2022-27778

* Wed May 25 2022 Suresh Babu Chalamalasetty <schalam@microsoft.com> - 7.83.0-1
- Update to version 7.83.0

* Mon Mar 07 2022 Andrew Phelps <anphel@microsoft.com> - 7.82.0-1
- Update to version 7.82.0

* Thu Dec 16 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 7.76.0-6
- Removing the explicit %%clean stage.

* Wed Jul 21 2021 Chris Co <chrco@microsoft.com> - 7.76.0-5
- Address CVE-2021-22922, CVE-2021-22923, CVE-2021-22924, CVE-2021-22925

* Thu Jun 24 2021 Suresh Babu Chalamalasetty <schalam@microsoft.com> - 7.76.0-4
- CVE-2021-22897 fix

* Fri May 28 2021 Daniel Burgener <daburgen@microsoft.com> - 7.76.0-3
- Disable check to remove circular dependency

* Wed May 26 2021 Jon Slobodzian <joslobo@microsoft.com> - 7.76.0-2 (from 1.0 branch)
- Patch 7.76.0 to fix CVE-2021-22898 and CVE-2021-22901.

* Fri Apr 02 2021 Thomas Crain <thcrain@microsoft.com> - 7.76.0-2 (from dev branch)
- Merge the following releases from dev to 1.0 spec
- v-ruyche@microsoft.com, 7.68.0-2: Add explicit provides for libcurl and libcurl-devel

* Wed Mar 31 2021 Nicolas Ontiveros <niontive@microsoft.com> - 7.76.0-1
- Upgrade to version 7.76.0 to fix CVE-2021-22876 and CVE-2021-22890.

* Tue Dec 22 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 7.74.0-1
- Updating to 7.74.0 to fix CVE-2020-8169 and incorporate fixes for other CVEs as well.
- Updating source URL to an HTTPS address.
- Enabling more tests to run by running them as non-root and extending 'BuildRequires'.
- License verified.

* Fri Dec 18 2020 Ruying Chen <v-ruyche@microsoft.com> - 7.68.0-5
- Patch CVE-2020-8231

* Tue Dec 15 2020 Ruying Chen <v-ruyche@microsoft.com> - 7.68.0-4
- Patch CVE-2020-8177

*   Wed Dec 09 2020 Nicolas Ontiveros <niontive@microsoft.com> 7.68.0-3
-   Patch CVE-2020-8284
-   Patch CVE-2020-8285
-   Patch CVE-2020-8286

*   Wed Oct 07 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 7.68.0-2
-   Updating certificate bundle path to include full set of trust information.

*   Tue Aug 11 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 7.68.0-1
-   Upgrading to 7.68.0 to enable verification against a partial cert chain.

*   Thu May 14 2020 Nicolas Ontiveros <niontive@microsoft.com> 7.66.0-1
-   Upgrade to version 7.66.0, which fixes CVE-2018-16890 and CVE-2019-3822/3833.

*   Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 7.61.1-6
-   Added %%license line automatically

*   Wed May 06 2020 Pawel Winogrodzki <pawelwi@microsoft.com> 7.61.1-5
-   Removing *Requires for "ca-certificates".
-   Adding a certs directory through "--with-ca-path" at compile time.

*   Mon Apr 20 2020 Nicolas Ontiveros <niontive@microsoft.com> 7.61.1-4
-   Fix CVE-2019-5481.
-   Fix CVE-2019-5482.
-   Remove sha1 macro.

*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 7.61.1-3
-   Initial CBL-Mariner import from Photon (license: Apache2).

*   Tue Jan 08 2019 Dweep Advani <dadvani@vmware.com> 7.61.1-2
-   Fix of CVE-2018-16839, CVE-2018-16840 and CVE-2018-16842

*   Mon Sep 10 2018 Ajay Kaher <akaher@vmware.com> 7.61.1-1
-   Upgraded to version 7.61.1

*   Wed Apr 04 2018 Dheeraj Shetty <dheerajs@vmware.com> 7.59.0-1
-   Update to version 7.59.0

*   Thu Feb 08 2018 Xiaolin Li <xiaolinl@vmware.com> 7.58.0-1
-   Fix CVE-2017-8817.

*   Thu Dec 21 2017 Xiaolin Li <xiaolinl@vmware.com> 7.56.1-2
-   Fix CVE-2017-8818.

*   Wed Dec 13 2017 Xiaolin Li <xiaolinl@vmware.com> 7.56.1-1
-   Update to version 7.56.1

*   Mon Nov 27 2017 Xiaolin Li <xiaolinl@vmware.com> 7.54.1-4
-   Fix CVE-2017-1000257

*   Mon Nov 06 2017 Xiaolin Li <xiaolinl@vmware.com> 7.54.1-3
-   Fix CVE-2017-1000254

*   Thu Nov 02 2017 Xiaolin Li <xiaolinl@vmware.com> 7.54.1-2
-   Fix CVE-2017-1000099, CVE-2017-1000100, CVE-2017-1000101

*   Tue Jul 11 2017 Divya Thaluru <dthaluru@vmware.com> 7.54.1-1
-   Update to 7.54.1

*   Mon Apr 24 2017 Bo Gan <ganb@vmware.com> 7.54.0-1
-   Update to 7.54.0

*   Fri Apr 14 2017 Alexey Makhalov <amakhalov@vmware.com> 7.51.0-5
-   Added -libs subpackage

*   Wed Dec 07 2016 Xiaolin Li <xiaolinl@vmware.com> 7.51.0-4
-   Added -devel subpackage.

*   Wed Nov 30 2016 Xiaolin Li <xiaolinl@vmware.com> 7.51.0-3
-   Enable sftp support.

*   Thu Nov 24 2016 Alexey Makhalov <amakhalov@vmware.com> 7.51.0-2
-   Required krb5-devel.

*   Wed Nov 02 2016 Anish Swaminathan <anishs@vmware.com> 7.51.0-1
-   Upgrade curl to 7.51.0

*   Wed Oct 05 2016 ChangLee <changlee@vmware.com> 7.50.3-2
-   Modified %check

*   Thu Sep 15 2016 Xiaolin Li <xiaolinl@vmware.com> 7.50.3-1
-   Update curl to version 7.50.3.

*   Tue Aug 23 2016 Xiaolin Li <xiaolinl@vmware.com> 7.47.1-3
-   Enable gssapi in curl.

*   Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 7.47.1-2
-   GA - Bump release of all rpms

*   Tue Feb 23 2016 Xiaolin Li <xiaolinl@vmware.com> 7.47.1-1
-   Updated to version 7.47.1

*   Thu Jan 14 2016 Xiaolin Li <xiaolinl@vmware.com> 7.46.0-1
-   Updated to version 7.46.0

*   Thu Aug 13 2015 Divya Thaluru <dthaluru@vmware.com> 7.43.0-1
-   Update to version 7.43.0.

*   Mon Apr 6 2015 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 7.41.0-1
-   Update to version 7.41.0.
