%global security_hardening nonow
%define glibc_target_cpu %{_build}
%define debug_package %{nil}
# Don't depend on bash by default
%define __requires_exclude ^/(bin|usr/bin).*$
Summary:        Main C library
Name:           glibc
Version:        2.28
Release:        21%{?dist}
License:        LGPLv2+
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Applications/System
URL:            https://www.gnu.org/software/libc
Source0:        https://ftp.gnu.org/gnu/glibc/%{name}-%{version}.tar.xz
Source1:        locale-gen.sh
Source2:        locale-gen.conf
Patch0:         http://www.linuxfromscratch.org/patches/downloads/glibc/glibc-2.25-fhs-1.patch
Patch1:         glibc-2.24-bindrsvport-blacklist.patch
Patch2:         0002-malloc-arena-fix.patch
Patch3:         glibc-2.28-CVE-2018-19591.patch
Patch4:         CVE-2019-9169.patch
Patch5:         CVE-2016-10739.patch
Patch6:         CVE-2020-1752.patch
Patch7:         CVE-2020-10029.patch
# Only applicable on ARMv7 targets.
Patch8:         CVE-2020-6096.nopatch
# Only applicable on x32 targets.
Patch9:         CVE-2019-6488.nopatch
# Only applicable on PowerPC targets.
Patch10:        CVE-2020-1751.nopatch
# Marked by upstream/Ubuntu/Red Hat as not a security bug, no fix available
# Rationale: Exploit requires crafted pattern in regex compiler meant only for trusted content
Patch11:        CVE-2018-20796.nopatch
Patch12:        CVE-2019-7309.patch
# CVE-2019-19126 patch taken from upstream commit 7966ce07e89fa4ccc8fdba00d4439fc652862462
Patch13:        CVE-2019-19126.patch
Patch14:        CVE-2019-25013.patch
Patch15:        CVE-2021-3326.patch
Patch16:        CVE-2020-27618.patch
Patch17:        CVE-2021-35942.patch
# CVE-2021-33574 is composed of two changes.  The original CVE fix -0001 for GLIBC 2.32 and a backport fix for GLIBC 2.28 -0002
Patch18:        CVE-2021-33574-0001.patch
Patch19:        CVE-2021-33574-0002.patch
# CVE-2021-38604 is as issues introduced with the original CVE-2021-33574 CVE.
Patch20:        CVE-2021-38604.patch
# pthread_cond_signal failed to wake up pthread_cond_wait
# Bug reference: https://bugs.launchpad.net/ubuntu/+source/glibc/+bug/1899800
# https://bugzilla.redhat.com/show_bug.cgi?id=1889892
# https://github.com/dotnet/runtime/issues/47700
# Patch path for reference:
# https://sourceware.org/bugzilla/attachment.cgi?id=12484&action=diff&collapsed=&headers=1&format=raw
Patch21:        glibc-2.28_pthread_cond_wait.patch
Requires:       filesystem
Provides:       rtld(GNU_HASH)
Provides:       /sbin/ldconfig
ExcludeArch:    armv7 ppc i386 i686

%description
This library provides the basic routines for allocating memory,
searching directories, opening and closing files, reading and
writing files, string handling, pattern matching, arithmetic,
and so on.

%package devel
Summary:        Header files for glibc
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description devel
These are the header files of glibc.

%package lang
Summary:        Additional language files for glibc
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description lang
These are the additional language files of glibc.

%package i18n
Summary:        Additional internationalization files for glibc
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description i18n
These are the additional internationalization files of glibc.

%package iconv
Summary:        gconv modules for glibc
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description iconv
These is gconv modules for iconv() and iconv tools.

%package tools
Summary:        tools for glibc
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description tools
Extra tools for glibc.

%package nscd
Summary:        Name Service Cache Daemon
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}

%description nscd
Name Service Cache Daemon

%prep
%autosetup -p1
sed -i 's/\\$$(pwd)/`pwd`/' timezone/Makefile
install -vdm 755 %{_builddir}/%{name}-build
# do not try to explicitly provide GLIBC_PRIVATE versioned libraries

%global __find_provides %{_builddir}/%{name}-%{version}/find_provides.sh
%global __find_requires %{_builddir}/%{name}-%{version}/find_requires.sh

# create find-provides and find-requires script in order to ignore GLIBC_PRIVATE errors
cat > find_provides.sh << _EOF
#! /bin/sh
if [ -d /tools ]; then
/tools/lib/rpm/find-provides | grep -v GLIBC_PRIVATE
else
%{_lib}/rpm/find-provides | grep -v GLIBC_PRIVATE
fi
exit 0
_EOF
chmod +x find_provides.sh

cat > find_requires.sh << _EOF
#! /bin/sh
if [ -d /tools ]; then
/tools/lib/rpm/find-requires %{buildroot} %{glibc_target_cpu} | grep -v GLIBC_PRIVATE
else
%{_lib}/rpm/find-requires %{buildroot} %{glibc_target_cpu} | grep -v GLIBC_PRIVATE
fi
_EOF
chmod +x find_requires.sh

%build
CFLAGS="`echo " %{build_cflags} " | sed 's/-Wp,-D_FORTIFY_SOURCE=2//'`"
CXXFLAGS="`echo " %{build_cxxflags} " | sed 's/-Wp,-D_FORTIFY_SOURCE=2//'`"
export CFLAGS
export CXXFLAGS

cd %{_builddir}/%{name}-build
../%{name}-%{version}/configure \
        --prefix=%{_prefix} \
        --disable-profile \
        --disable-werror \
        --enable-kernel=3.2 \
        --enable-bind-now \
        --disable-experimental-malloc \
%ifarch x86_64
        --enable-cet \
%endif
        --disable-silent-rules

# Sometimes we have false "out of memory" make error
# just rerun/continue make to work around it.
make %{?_smp_mflags} || make %{?_smp_mflags} || make %{?_smp_mflags}

%install
#       Do not remove static libs
pushd %{_builddir}/glibc-build
#       Create directories
make install_root=%{buildroot} install
install -vdm 755 %{buildroot}%{_sysconfdir}/ld.so.conf.d
install -vdm 755 %{buildroot}%{_var}/cache/nscd
install -vdm 755 %{buildroot}%{_libdir}/locale
cp -v ../%{name}-%{version}/nscd/nscd.conf %{buildroot}%{_sysconfdir}/nscd.conf
#       Install locale generation script and config file
cp -v %{SOURCE2} %{buildroot}%{_sysconfdir}
cp -v %{SOURCE1} %{buildroot}/sbin
#       Remove unwanted cruft
rm -rf %{buildroot}%{_infodir}
#       Install configuration files

# Spaces should not be used in nsswitch.conf in the begining of new line
# Only tab should be used as it expects the same in source code.
# Otherwise "altfiles" will not be added. which may cause dbus.service failure
cat > %{buildroot}%{_sysconfdir}/nsswitch.conf <<- "EOF"
#       Begin /etc/nsswitch.conf

	passwd: files
	group: files
	shadow: files

	hosts: files dns
	networks: files

	protocols: files
	services: files
	ethers: files
	rpc: files
#       End /etc/nsswitch.conf
EOF
cat > %{buildroot}%{_sysconfdir}/ld.so.conf <<- "EOF"
#       Begin /etc/ld.so.conf
	%{_prefix}/local/lib
	/opt/lib
	include %{_sysconfdir}/ld.so.conf.d/*.conf
EOF
popd
%find_lang %{name} --all-name
pushd localedata
# Generate out of locale-archive an (en_US.) UTF-8 locale
mkdir -p %{buildroot}%{_lib}/locale
I18NPATH=. GCONV_PATH=../../glibc-build/iconvdata LC_ALL=C ../../glibc-build/locale/localedef --no-archive --prefix=%{buildroot} -A ../intl/locale.alias -i locales/en_US -c -f charmaps/UTF-8 en_US.UTF-8
mv %{buildroot}%{_lib}/locale/en_US.utf8 %{buildroot}%{_lib}/locale/en_US.UTF-8
popd
# to do not depend on /bin/bash
sed -i 's@#! /bin/bash@#! /bin/sh@' %{buildroot}%{_bindir}/ldd
sed -i 's@#!/bin/bash@#!/bin/sh@' %{buildroot}%{_bindir}/tzselect

%check
cd %{_builddir}/glibc-build
make %{?_smp_mflags} check ||:
# These 2 persistant false positives are OK
# XPASS for: elf/tst-protected1a and elf/tst-protected1b
[ `grep ^XPASS tests.sum | wc -l` -ne 2 -a `grep "^XPASS: elf/tst-protected1[ab]" tests.sum | wc -l` -ne 2 ] && exit 1 ||:

# FAIL (intermittent) in chroot but PASS in container:
# posix/tst-spawn3 and stdio-common/test-vfprintf
n=0
grep "^FAIL: posix/tst-spawn3" tests.sum >/dev/null && n=$((n+1)) ||:
grep "^FAIL: stdio-common/test-vfprintf" tests.sum >/dev/null && n=$((n+1)) ||:
# FAIL always on overlayfs/aufs (in container)
grep "^FAIL: posix/tst-dir" tests.sum >/dev/null && n=$((n+1)) ||:

#https://sourceware.org/glibc/wiki/Testing/Testsuite
grep "^FAIL: nptl/tst-eintr1" tests.sum >/dev/null && n=$((n+1)) ||:
#This happens because the kernel fails to reap exiting threads fast enough,
#eventually resulting an EAGAIN when pthread_create is called within the test.

# check for exact 'n' failures
[ `grep ^FAIL tests.sum | wc -l` -ne $n ] && exit 1 ||:

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%license LICENSES
%{_libdir}/locale/*
%dir %{_sysconfdir}/ld.so.conf.d
%config(noreplace) %{_sysconfdir}/nsswitch.conf
%config(noreplace) %{_sysconfdir}/ld.so.conf
%config(noreplace) %{_sysconfdir}/rpc
%config(missingok,noreplace) %{_sysconfdir}/ld.so.cache
%config %{_sysconfdir}/locale-gen.conf
/lib64/*
%ifarch aarch64
%exclude /lib
%endif
%{_lib64dir}/*.so
%{_lib64dir}/audit/*
/sbin/ldconfig
/sbin/locale-gen.sh
%{_bindir}/*
%{_libexecdir}/*
%{_datadir}/i18n/charmaps/UTF-8.gz
%{_datadir}/i18n/charmaps/ISO-8859-1.gz
%{_datadir}/i18n/locales/en_US
%{_datarootdir}/locale/locale.alias
%exclude %{_localstatedir}/lib/nss_db/Makefile
%exclude %{_bindir}/catchsegv
%exclude %{_bindir}/iconv
%exclude %{_bindir}/mtrace
%exclude %{_bindir}/pcprofiledump
%exclude %{_bindir}/pldd
%exclude %{_bindir}/sotruss
%exclude %{_bindir}/sprof
%exclude %{_bindir}/xtrace

%files iconv
%defattr(-,root,root)
%{_lib64dir}/gconv/*
%{_bindir}/iconv
%{_sbindir}/iconvconfig

%files tools
%defattr(-,root,root)
%{_bindir}/catchsegv
%{_bindir}/mtrace
%{_bindir}/pcprofiledump
%{_bindir}/pldd
%{_bindir}/sotruss
%{_bindir}/sprof
%{_bindir}/xtrace
%{_sbindir}/zdump
%{_sbindir}/zic
/sbin/sln

%files nscd
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/nscd.conf
%{_sbindir}/nscd
%dir %{_localstatedir}/cache/nscd

%files i18n
%defattr(-,root,root)
%{_datadir}/i18n/charmaps/*.gz
%{_datadir}/i18n/locales/*
%exclude %{_datadir}/i18n/charmaps/UTF-8.gz
%exclude %{_datadir}/i18n/charmaps/ISO-8859-1.gz
%exclude %{_datadir}/i18n/locales/en_US

%files devel
%defattr(-,root,root)
# TODO: Excluding for now to remove dependency on PERL
# /usr/bin/mtrace
%{_lib64dir}/*.a
%{_lib64dir}/*.o
%{_includedir}/*

%files -f %{name}.lang lang
%defattr(-,root,root)

%changelog
* Thu Nov 04 2021 Suresh Babu Chalamalasetty <schalam@microsoft.com> - 2.28-21
- Patch for glibc pthread_cond_signal failed to wake up pthread_cond_wait issue.

* Mon Sep 06 2021 Jon Slobodzian <joslobo@microsoft.com> - 2.28-20
- Patch CVE-2021-33574 and nopatch CVE-2021-38604.

* Tue Aug 03 2021 Nicolas guibourge <nicolasg@microsoft.com> - 2.28-19
- Patch CVE-2021-35942

* Mon Mar 22 2021 Nick Samson <nisamson@microsoft.com> - 2.28-18
- Patch CVE-2020-27618

* Tue Feb 09 2021 Thomas Crain <thcrain@microsoft.com> - 2.28-17
- Patch CVE-2021-3326

* Fri Jan 08 2021 Nicolas guibourge <nicolasg@microsoft.com> - 2.28-16
- Patch CVE-2019-25013

* Mon Dec 07 2020 Mateusz Malisz <mamalisz@microsoft.com> - 2.28-15
- Exclude binaries(such as bash) from requires list.

* Tue Nov 10 2020 Thomas Crain <thcrain@microsoft.com> - 2.28-14
- Patch CVE-2019-19126

* Wed Oct 28 2020 Henry Li <lihl@microsoft.com> - 2.28-13
- Used autosetup
- Added patch to resolve CVE-2019-7309

* Wed Jul 29 2020 Thomas Crain <thcrain@microsoft.com> - 2.28-12
- Ignore CVE-2018-20796, as it is not a security issue

* Wed Jul 29 2020 Emre Girgin <mrgirgin@microsoft.com> - 2.28-11
- Disable the debuginfo package for glibc, and use unstripped binaries instead.

* Fri Jun 26 2020 Ruying Chen <v-ruyche@microsoft.com> - 2.28-10
- Added provides for binary capability.

* Thu Jun 11 2020 Henry Beberman <henry.beberman@microsoft.com> - 2.28-9
- Disable -Wp,-D_FORTIFY_SOURCE=2 to build with hardened cflags.

* Tue May 19 2020 Emre Girgin <mrgirgin@microsoft.com> - 2.28-8
- Ignore CVE-2019-6488, CVE-2020-1751, CVE-2020-6096 as they don't apply to aarch64 or x86_64.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 2.28-7
- Added %%license line automatically

* Fri Mar 20 2020 Andrew Phelps <anphel@microsoft.com> - 2.28-6
- Configure with --disable-werror.

* Mon Dec 02 2019 Saravanan Somasundaram <sarsoma@microsoft.com> - 2.28-5
- Initial CBL-Mariner import from Photon (license: Apache2).

* Fri Jul 12 2019 Ankit Jain <ankitja@vmware.com> - 2.28-4
- Replaced spaces with tab in nsswitch.conf file

* Fri Mar 08 2019 Alexey Makhalov <amakhalov@vmware.com> - 2.28-3
- Fix CVE-2019-9169

* Tue Jan 22 2019 Anish Swaminathan <anishs@vmware.com> - 2.28-2
- Fix CVE-2018-19591

* Tue Aug 28 2018 Alexey Makhalov <amakhalov@vmware.com> - 2.28-1
- Version update. Disable obsolete rpc (use libtirpc) and nsl.

* Tue Jan 23 2018 Xiaolin Li <xiaolinl@vmware.com> - 2.26-10
- Fix CVE-2018-1000001 and CVE-2018-6485

* Mon Jan 08 2018 Xiaolin Li <xiaolinl@vmware.com> - 2.26-9
- Fix CVE-2017-16997

* Thu Dec 21 2017 Xiaolin Li <xiaolinl@vmware.com> - 2.26-8
- Fix CVE-2017-17426

* Tue Nov 14 2017 Alexey Makhalov <amakhalov@vmware.com> - 2.26-7
- Aarch64 support

* Wed Oct 25 2017 Xiaolin Li <xiaolinl@vmware.com> - 2.26-6
- Fix CVE-2017-15670 and CVE-2017-15804

* Tue Oct 10 2017 Alexey Makhalov <amakhalov@vmware.com> - 2.26-5
- Compile out tcache.

* Fri Sep 15 2017 Bo Gan <ganb@vmware.com> - 2.26-4
- exclude tst-eintr1 per official wiki recommendation.

* Tue Sep 12 2017 Alexey Makhalov <amakhalov@vmware.com> - 2.26-3
- Fix makecheck for run in docker.

* Tue Aug 29 2017 Alexey Makhalov <amakhalov@vmware.com> - 2.26-2
- Fix tunables setter.
- Add malloc arena fix.
- Fix makecheck.

* Tue Aug 15 2017 Alexey Makhalov <amakhalov@vmware.com> - 2.26-1
- Version update

* Tue Aug 08 2017 Anish Swaminathan <anishs@vmware.com> - 2.25-4
- Apply fix for CVE-2017-1000366

* Thu May 4  2017 Bo Gan <ganb@vmware.com> - 2.25-3
- Remove bash dependency in post/postun script

* Fri Apr 21 2017 Alexey Makhalov <amakhalov@vmware.com> - 2.25-2
- Added -iconv -tools and -nscd subpackages

* Wed Mar 22 2017 Alexey Makhalov <amakhalov@vmware.com> - 2.25-1
- Version update

* Wed Dec 14 2016 Alexey Makhalov <amakhalov@vmware.com> - 2.24-1
- Version update

* Wed Nov 23 2016 Alexey Makhalov <amakhalov@vmware.com> - 2.22-13
- Install en_US.UTF-8 locale by default

* Wed Nov 16 2016 Alexey Makhalov <amakhalov@vmware.com> - 2.22-12
- Added i18n subpackage

* Tue Oct 25 2016 Alexey Makhalov <amakhalov@vmware.com> - 2.22-11
- Workaround for build failure with "out of memory" message

* Wed Sep 28 2016 Alexey Makhalov <amakhalov@vmware.com> - 2.22-10
- Added pthread_create-fix-use-after-free.patch

* Tue Jun 14 2016 Divya Thaluru <dthaluru@vmware.com> - 2.22-9
- Enabling rpm debug package and stripping the libraries

* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 2.22-8
- GA - Bump release of all rpms

* Mon May 23 2016 Divya Thaluru <dthaluru@vmware.com> - 2.22-7
- Added patch for CVE-2014-9761

* Mon Mar 21 2016 Alexey Makhalov <amakhalov@vmware.com> - 2.22-6
- Security hardening: nonow

* Fri Mar 18 2016 Anish Swaminathan <anishs@vmware.com> - 2.22-5
- Change conf file qualifiers

* Fri Mar 11 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 2.22-4
- Added patch for res_qeury assertion with bad dns config
- Details: https://sourceware.org/bugzilla/show_bug.cgi?id=19791

* Tue Feb 16 2016 Anish Swaminathan <anishs@vmware.com> - 2.22-3
- Added patch for CVE-2015-7547

* Mon Feb 08 2016 Anish Swaminathan <anishs@vmware.com> - 2.22-2
- Added patch for bindresvport blacklist

* Tue Jan 12 2016 Xiaolin Li <xiaolinl@vmware.com> - 2.22-1
- Updated to version 2.22

* Tue Dec 1 2015 Divya Thaluru <dthaluru@vmware.com> - 2.19-8
- Disabling rpm debug package and stripping the libraries

* Wed Nov 18 2015 Divya Thaluru <dthaluru@vmware.com> - 2.19-7
- Adding patch to close nss files database

* Tue Nov 10 2015 Xiaolin Li <xiaolinl@vmware.com> - 2.19-6
- Handled locale files with macro find_lang

* Wed Aug 05 2015 Kumar Kaushik <kaushikk@vmware.com> - 2.19-5
- Adding postun section for ldconfig.

* Tue Jul 28 2015 Alexey Makhalov <amakhalov@vmware.com> - 2.19-4
- Support glibc building against current rpm version.

* Thu Jul 23 2015 Divya Thaluru <dthaluru@vmware.com> - 2.19-3
- Packing locale-gen scripts

* Mon May 18 2015 Touseef Liaqat <tliaqat@vmware.com> - 2.19-2
- Update according to UsrMove.

* Wed Nov 5 2014 Divya Thaluru <dthaluru@vmware.com> - 2.19-1
- Initial build. First version
