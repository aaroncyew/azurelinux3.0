# Copyright © INRIA 2009-2010
# Brice Goglin <Brice.Goglin@inria.fr>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# KMP is disabled by default
%{!?KMP: %global KMP 0}

%{!?_release: %global _release OFED.5.6.0.1.6.1}
%global kver %(/bin/rpm -q --queryformat '%{RPMTAG_VERSION}-%{RPMTAG_RELEASE}' $(/bin/rpm -q --whatprovides kernel-devel))
%global ksrc %{_libdir}/modules/%{kver}/build
%global moddestdir %{buildroot}%{_libdir}/modules/%{kver}/kernel/
%global kernel_version %{kver}
%global krelver %(echo -n %{kver} | sed -e 's/-/_/g')
%global _kmp_rel %{_release}%{?_kmp_build_num}%{?_dist}

# set package name
%{!?_name: %global _name knem}

Summary:        KNEM: High-Performance Intra-Node MPI Communication
Name:           knem
Version:        1.1.4.90mlnx1
Release:        1%{?dist}
License:        BSD and GPLv2
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Libraries
Source:         https://linux.mellanox.com/public/repo/bluefield/3.9.0/extras/mlnx_ofed/5.6-1.0.3.3/SOURCES/knem_1.1.4.90mlnx1.orig.tar.gz#/%{name}-%{version}.tar.gz
BuildRequires:  kernel-devel
BuildRequires:  kmod
Requires:       kernel
Provides:       knem-mlnx = %{version}-%{release}
Obsoletes:      knem-mlnx < %{version}-%{release}

%description
KNEM is a Linux kernel module enabling high-performance intra-node MPI communication for large messages. KNEM offers support for asynchronous and vectorial data transfers as well as offloading memory copies on to Intel I/OAT hardware.
See http://knem.gitlabpages.inria.fr for details.

%global debug_package %{nil}

# build KMP rpms?
%if "%{KMP}" == "1"
%global kernel_release() $(make -C %{1} M=$PWD kernelrelease | grep -v make)
BuildRequires: %kernel_module_package_buildreqs
# prep file list for kmp rpm
%(cat > %{_builddir}/kmp.files << EOF
%defattr(644,root,root,755)
/lib/modules/%2-%1
%if %{IS_RHEL_VENDOR}
%config(noreplace) %{_sysconfdir}/depmod.d/%{_name}.conf
%endif
EOF)
%(cat > %{_builddir}/preamble << EOF
Obsoletes: kmod-knem-mlnx < %{version}-%{release}
Obsoletes: knem-mlnx-kmp-default < %{version}-%{release}
Obsoletes: knem-mlnx-kmp-trace < %{version}-%{release}
Obsoletes: knem-mlnx-kmp-xen < %{version}-%{release}
Obsoletes: knem-mlnx-kmp-trace < %{version}-%{release}
Obsoletes: knem-mlnx-kmp-ppc64 < %{version}-%{release}
Obsoletes: knem-mlnx-kmp-ppc < %{version}-%{release}
Obsoletes: knem-mlnx-kmp-smp < %{version}-%{release}
Obsoletes: knem-mlnx-kmp-pae < %{version}-%{release}
EOF)
%{kernel_module_package -f %{_builddir}/kmp.files -p %{_builddir}/preamble -r %{_kmp_rel} }
%else 

%global kernel_source() %{ksrc}
%global kernel_release() %{kver}
%global flavors_to_build default
%global release_full %{_release}.%{kver}.%{krelver}

%package modules
Summary: KNEM: High-Performance Intra-Node MPI Communication
Group: System Environment/Libraries
%description modules
KNEM is a Linux kernel module enabling high-performance intra-node MPI communication for large messages. KNEM offers support for asynchronous and vectorial data transfers as well as loading memory copies on to Intel I/OAT hardware.
See http://runtime.bordeaux.inria.fr/knem/ for details.
%endif #end if "%{KMP}" == "1"

#
# setup module sign scripts if paths to the keys are given
#
# %global WITH_MOD_SIGN %(if ( test -f "$MODULE_SIGN_PRIV_KEY" && test -f "$MODULE_SIGN_PUB_KEY" ); \
# 	then \
# 		echo -n '1'; \
# 	else \
# 		echo -n '0'; fi)

# %if "%{WITH_MOD_SIGN}" == "1"
# # call module sign script
# %global __modsign_install_post \
#     $RPM_BUILD_DIR/knem-%{version}/source/tools/sign-modules %{buildroot}/lib/modules/ %{kernel_source default} || exit 1 \
# %{nil}

# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
# %global __spec_install_post \
#   %{?__debug_package:%{__debug_install_post}} \
#   %{__arch_install_post} \
#   %{__os_install_post} \
#   %{__modsign_install_post} \
# %{nil}

# %endif # end of setup module sign scripts
# #

%global install_mod_dir extra/%{_name}


%prep
%autosetup -p1 -n knem-%{version}
set -- *
mkdir source
mv "$@" source/
mkdir obj

%build
export INSTALL_MOD_DIR=%{install_mod_dir}
for flavor in %flavors_to_build; do
	export KSRC=%{kernel_source $flavor}
	export K_BUILD=%{kernel_source $flavor}
	export KVER=%{kernel_release $K_BUILD}
	export LIB_MOD_DIR=/lib/modules/$KVER/$INSTALL_MOD_DIR
	export MODULE_DESTDIR=/lib/modules/$KVER/$INSTALL_MOD_DIR
	rm -rf obj/$flavor
	cp -a source obj/$flavor
	cd $PWD/obj/$flavor
	find . -type f -exec touch -t 200012201010 '{}' \; || true
	./configure --prefix=/opt/knem-%{version} --with-linux-release=$KVER --with-linux=/lib/modules/$KVER/source --with-linux-build=$KSRC --libdir=/opt/knem-%{version}/lib
	make
	cd -
done

%install
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=%install_mod_dir
export KPNAME=%{_name}
mkdir -p %{buildroot}/etc/udev/rules.d
install -d %{buildroot}/usr/lib64/pkgconfig
for flavor in %flavors_to_build; do
	cd $PWD/obj/$flavor
	export KSRC=%{kernel_source $flavor}
	export K_BUILD=%{kernel_source $flavor}
	export KVER=%{kernel_release $K_BUILD}
	make DESTDIR=%{buildroot} install KERNELRELEASE=$KVER
	export MODULE_DESTDIR=/lib/modules/$KVER/$INSTALL_MOD_DIR
	mkdir -p %{buildroot}/lib/modules/$KVER/$INSTALL_MOD_DIR
	MODULE_DESTDIR=/lib/modules/$KVER/$INSTALL_MOD_DIR DESTDIR=%{buildroot} KVERSION=$KVER %{buildroot}/opt/knem-%{version}/sbin/knem_local_install
	cp knem.pc  %{buildroot}/usr/lib64/pkgconfig
	cd -
done

/bin/rm -rf %{buildroot}/opt/knem-%{version}/lib/modules || true

# Set the module(s) to be executable, so that they will be stripped when packaged.
find %{buildroot} \( -type f -name '*.ko' -o -name '*ko.gz' \) -exec %{__strip} -p --strip-debug --discard-locals -R .comment -R .note \{\} \;

%post
getent group rdma >/dev/null 2>&1 || groupadd -r rdma
touch /etc/udev/rules.d/10-knem.rules
# load knem
/sbin/modprobe -r knem > /dev/null 2>&1
/sbin/modprobe knem > /dev/null 2>&1

# automatically load knem onboot
if [ -d /etc/sysconfig/modules ]; then
	# RH
	echo "/sbin/modprobe knem > /dev/null 2>&1" > /etc/sysconfig/modules/knem.modules
	chmod +x /etc/sysconfig/modules/knem.modules
elif [ -e /etc/sysconfig/kernel ]; then
	# SLES
	if ! (grep -w knem /etc/sysconfig/kernel); then
		sed -i -r -e 's/^(MODULES_LOADED_ON_BOOT=)"(.*)"/\1"\2 knem"/' /etc/sysconfig/kernel
	fi
fi

%preun
# unload knem
/sbin/modprobe -r knem > /dev/null 2>&1
# RH
/bin/rm -f /etc/sysconfig/modules/knem.modules
# SLES
if (grep -qw knem /etc/sysconfig/kernel 2>/dev/null); then
	sed -i -e 's/ knem//g' /etc/sysconfig/kernel 2>/dev/null
fi

%if "%{KMP}" != "1"
%post modules
depmod %{kver} -a

%postun modules
if [ $1 = 0 ]; then  # 1 : Erase, not upgrade
	depmod %{kver} -a
fi
%endif # end KMP!=1

%files
%defattr(-, root, root)
%license COPYING COPYING.BSD-3 COPYING.GPL-2
/opt/knem-%{version}
/usr/lib64/pkgconfig/knem.pc
%config(noreplace)
/etc/udev/rules.d/10-knem.rules

%if "%{KMP}" != "1"
%files modules
/lib/modules/%{kver}/%{install_mod_dir}/
%endif

%changelog
* Fri Jul 22 2022 Rachel Menge <rachelmenge@microsoft.com> 1.1.4.90mlnx1-1
- Initial CBL-Mariner import from NVIDIA (license: ASL 2.0).
- Lint spec to conform to Mariner 
- License verified

* Mon Mar 17 2014 Alaa Hleihel <alaa@mellanox.com>
- Use one spec for KMP and non-KMP OS's.

* Thu Apr 18 2013 Alaa Hleihel <alaa@mellanox.com>
- Added KMP support
