%global with_debug 0
# We want verbose builds
%global _configure_disable_silent_rules 1
# Shamelessly copied from CRI-O spec file.
%if 0%{?with_debug}
%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package %{nil}
%endif
# https://github.com/rust-lang/rust/issues/47714
%undefine _strict_symbol_defs_build

%global katacache               %{_localstatedir}/cache
%global katalibexecdir          %{_libexecdir}/kata-containers
%global katalocalstatecachedir  %{katacache}/kata-containers

%global kataagentdir            %{katalibexecdir}/agent
%global kataosbuilderdir        %{katalibexecdir}/osbuilder

%global runtime_make_vars       QEMUPATH=%{qemupath} \\\
                                KERNELTYPE="compressed" \\\
                                KERNELPARAMS="systemd.legacy_systemd_cgroup_controller=yes systemd.unified_cgroup_hierarchy=0" \\\
                                DEFSHAREDFS="virtio-fs" \\\
                                DEFVIRTIOFSDAEMON=%{_libexecdir}/"virtiofsd" \\\
                                DEFVIRTIOFSCACHESIZE=0 \\\
                                DEFSANDBOXCGROUPONLY=false \\\
                                DEFSTATICSANDBOXWORKLOADMEM=1984 \\\
                                DEFMEMSZ=64 \\\
                                SKIP_GO_VERSION_CHECK=y \\\
                                MACHINETYPE=%{machinetype} \\\
                                DESTDIR=%{buildroot} \\\
                                PREFIX=/usr \\\
                                FEATURE_SELINUX="yes" \\\
                                DEFENABLEANNOTATIONS=['\\\".*\\\"'] \\\
                                DEFAULT_HYPERVISOR=cloud-hypervisor

%global agent_make_vars         LIBC=gnu \\\ #todo: experiment with 
                                DESTDIR=%{buildroot}%{kataagentdir}
                                # todo: double check -ldflags="-s -w" is inherited as expected

Summary:        Kata Containers version 2.x repository
Name:           kata-containers
Version:        3.1.0
Release:        1%{?dist}
License:        ASL 2.0
Vendor:         Microsoft Corporation
URL:            https://github.com/%{name}/%{name}
Source0:        https://github.com/%{name}/%{name}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        https://github.com/%{name}/%{name}/releases/download/%{version}/%{name}-%{version}-vendor.tar.gz
Source2:        kata-osbuilder.sh
Source3:        kata-osbuilder-generate.service
Source4:        15-dracut.conf
Source5:        50-kata
Patch0:         0001-Merged-PR-9607-Allow-10-seconds-for-VM-creation-star.patch
Patch1:         0002-Merged-PR-9671-Wait-for-a-possibly-slow-Guest.patch
Patch2:         0003-Merged-PR-9805-Add-support-for-MSHV.patch
Patch3:         0004-Merged-PR-9806-Fix-enable_debug-for-hypervisor.clh.patch
Patch4:         0005-Merged-PR-9956-shim-avoid-memory-hotplug-timeout.patch
Patch9:         runtime-reduce-uvm-high-mem-footprint.patch

BuildRequires:  golang
BuildRequires:  git-core
BuildRequires:  libselinux-devel
BuildRequires:  libseccomp-devel
BuildRequires:  make
BuildRequires:  systemd
BuildRequires:  gcc
BuildRequires:  protobuf-compiler
BuildRequires:  mariner-release
BuildRequires:  dracut
BuildRequires:  kernel
BuildRequires:  busybox
BuildRequires:  cargo
BuildRequires:  rust

Requires:       busybox
Requires:       dracut
Requires:       kernel
Requires:       libseccomp
Requires:       qemu-kvm-core >= 4.2.0-4
Requires:       %{_libexecdir}/virtiofsd

Conflicts:      kata-agent
Conflicts:      kata-ksm-throttler
Conflicts:      kata-osbuilder
Conflicts:      kata-proxy
Conflicts:      kata-runtime
Conflicts:      kata-shim

%description
Kata Containers version 2.x repository. Kata Containers is an open source
project and community working to build a standard implementation of lightweight
Virtual Machines (VMs) that feel and perform like containers, but provide the
workload isolation and security advantages of VMs. https://katacontainers.io/.}

%prep
%autosetup -p1 -n %{name}-%{version}

cd %{_builddir}/%{name}-%{version}
tar -xf %{SOURCE1}

# Not using gobuild here in order to stick to how upstream builds
# (This builds multiple binaries)
%build
export PATH=$PATH:"$(pwd)/go/bin"
export GOPATH="$(pwd)/go"

mkdir -p go/src/github.com/%{name}
ln -s $(pwd)/../%{name}-%{version} go/src/github.com/%{name}/%{name}
cd go/src/github.com/%{name}/%{name}

pushd src/runtime
%make_build %{runtime_make_vars}
popd

pushd src/agent
make optimize %{agent_make_vars}
touch kata-agent
popd

pushd tools/osbuilder
# Manually build nsdax tool
gcc %{build_cflags} image-builder/nsdax.gpl.c -o nsdax
popd

# Not using gopkginstall here in order to stick to how upstream builds
%install
export GOPATH=$(pwd)/go
export PATH=$PATH:$GOPATH/bin

cd go/src/github.com/%{name}/%{name}

install -m 0644 -D -t %{buildroot}%{katalibexecdir} VERSION

pushd src/runtime
%make_install %{runtime_make_vars}
popd

pushd src/agent
%make_install %{agent_make_vars}
popd

pushd tools/osbuilder
rm .gitignore
rm rootfs-builder/.gitignore
mkdir -p %{buildroot}%{katalocalstatecachedir}

install -m 0644 -D -t %{buildroot}%{_unitdir} %{SOURCE3}
install -m 0755 -D -t %{buildroot}%{kataosbuilderdir} nsdax
install -m 0644 -D -t %{buildroot}%{kataosbuilderdir} %{SOURCE2}

cp -aR rootfs-builder %{buildroot}%{kataosbuilderdir}
cp -aR image-builder  %{buildroot}%{kataosbuilderdir}
cp -aR initrd-builder %{buildroot}%{kataosbuilderdir}
cp -aR scripts        %{buildroot}%{kataosbuilderdir}
cp -aR dracut         %{buildroot}%{kataosbuilderdir}

rm -f %{buildroot}%{kataosbuilderdir}/image-builder/nsdax.gpl.c
install -m 0644 -D -t %{buildroot}%{kataosbuilderdir}/dracut/dracut.conf.d/ %{SOURCE4}
chmod +x %{buildroot}%{kataosbuilderdir}/scripts/lib.sh
chmod +x %{buildroot}%{kataosbuilderdir}/kata-osbuilder.sh
popd

# Install the CRI-O config drop-in file
install -m 0644 -D -t %{buildroot}%{_sysconfdir}/crio/crio.conf.d %{SOURCE5}

# Disable the image= option, so we use initrd= by default
# The kernels kata-osbuilder creates are in /var/cache now, see rhbz#1792216

# Make symlinks in /usr/local/bin to /usr/bin where kata expects to find binaries
mkdir -p %{buildroot}%{_prefix}/local/bin
ln -sf %{_bindir}/containerd-shim-kata-v2 %{buildroot}%{_prefix}/local/bin/containerd-shim-kata-v2
ln -sf %{_bindir}/kata-monitor %{buildroot}%{_prefix}/local/bin/kata-monitor
ln -sf %{_bindir}/kata-runtime %{buildroot}%{_prefix}/local/bin/kata-runtime

%preun
%systemd_preun kata-osbuilder-generate.service

%postun
%systemd_postun kata-osbuilder-generate.service

%post
%systemd_post kata-osbuilder-generate.service

%files
# runtime
%{_bindir}/containerd-shim-kata-v2
%{_bindir}/kata-monitor
%{_bindir}/kata-runtime
%{_bindir}/kata-collect-data.sh
%{_prefix}/local/bin/containerd-shim-kata-v2
%{_prefix}/local/bin/kata-monitor
%{_prefix}/local/bin/kata-runtime
%dir %{_datadir}/defaults/kata-containers/
%{_datadir}/defaults/kata-containers/configuration*.toml
%dir %{katalibexecdir}
%{katalibexecdir}/VERSION
%{_datadir}/bash-completion/completions/kata-runtime
%license LICENSE
%doc CONTRIBUTING.md
%doc README.md

#agent
%dir %{kataagentdir}
%{kataagentdir}/*

#osbuilder
%dir %{kataosbuilderdir}
%dir %{katalocalstatecachedir}

%{kataosbuilderdir}/*
%{_unitdir}/kata-osbuilder-generate.service

# CRI-O drop-in file
%{_sysconfdir}/crio/crio.conf.d/50-kata

# Remove some scripts we don't use
%exclude %{kataosbuilderdir}/rootfs-builder/alpine
%exclude %{kataosbuilderdir}/rootfs-builder/centos
%exclude %{kataosbuilderdir}/rootfs-builder/clearlinux
%exclude %{kataosbuilderdir}/rootfs-builder/debian
%exclude %{kataosbuilderdir}/rootfs-builder/template
%exclude %{kataosbuilderdir}/rootfs-builder/ubuntu

%changelog
* Wed Apr 12 2023 Saul Paredes <saulparedes@microsoft.com> - 3.1.0-1
- Update to version 3.1.0

* Wed Apr 5 2023 Saul Paredes <saulparedes@microsoft.com> - 3.0.0-9
- Update kernel uvm image location

* Wed Apr 05 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 3.0.0-8
- Bump release to rebuild with go 1.19.8

* Tue Mar 28 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 3.0.0-7
- Bump release to rebuild with go 1.19.7

* Wed Mar 22 2023 Manuel Huber <mahuber@microsoft.com> - 3.0.0-6
- Integrate fix to reduce UVM memory consumption

* Wed Mar 15 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 3.0.0-5
- Bump release to rebuild with go 1.19.6

* Fri Feb 03 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 3.0.0-4
- Bump release to rebuild with go 1.19.5

* Wed Jan 18 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 3.0.0-3
- Bump release to rebuild with go 1.19.4

* Fri Dec 16 2022 Daniel McIlvaney <damcilva@microsoft.com> - 3.0.0-2
- Bump release to rebuild with go 1.18.8 with patch for CVE-2022-41717

* Tue Nov 15 2022 Neha Agarwal <nehaagarwal@microsoft.com> - 3.0.0-1
- Update to v3.0.0, apply patches for compatibility with Cloud-hypervisor v27.0.60.

* Tue Nov 01 2022 Olivia Crain <oliviacrain@microsoft.com> - 2.5.0-7
- Bump release to rebuild with go 1.18.8

* Thu Sep 15 2022 Neha Agarwal <nehaagarwal@microsoft.com> - 2.5.0-6
- Add patch to avoid memory hotplug timeout, add libseccomp.

* Mon Sep 12 2022 Neha Agarwal <nehaagarwal@microsoft.com> - 2.5.0-5
- Generate initrd on reload.

* Tue Sep 06 2022 Neha Agarwal <nehaagarwal@microsoft.com> - 2.5.0-4
- Set DEFSANDBOXCGROUPONLY="false".

* Wed Sep 02 2022 Neha Agarwal <nehaagarwal@microsoft.com> - 2.5.0-3
- Add kernel config to match guest and host cgroup setup.
- Add patch to expose devices from kata.

* Wed Aug 31 2022 Andrew Phelps <anphel@microsoft.com> - 2.5.0-2
- Fix arm64 build issue by excluding configuration-acrn.toml

* Fri Aug 19 2022 Neha Agarwal <nehaagarwal@microsoft.com> - 2.5.0-1
- Initial CBL-Mariner import from Fedora 37 (license: MIT).
- License verified.

* Thu Jul 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.2-1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Sat Jun 18 2022 Robert-AndrĂ© Mauchin <zebob.m@gmail.com> - 2.4.2-1.1
- Rebuilt for CVE-2022-1996, CVE-2022-24675, CVE-2022-28327, CVE-2022-27191,
  CVE-2022-29526, CVE-2022-30629

* Tue Jun 14 2022 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.4.2-1
- kata-containers-2.4.2

* Thu May 12 2022 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.4.1-1
- kata-containers-2.4.1

* Fri Apr 01 2022 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.4.0-1
- kata-containers-2.4.0

* Wed Mar 09 2022 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.3.3-1
- kata-containers-2.3.3

* Thu Feb 10 2022 Cole Robinson <crobinso@redhat.com> - 2.3.2-2
- Add explicit dep on /usr/libexec/virtiofsd

* Thu Feb 03 2022 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.3.2-1
- kata-containers-2.3.2

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.0-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Nov 29 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.3.0-1
- kata-containers-2.3.0

* Mon Nov 08 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.2.3-1
- kata-containers-2.2.3

* Mon Oct 18 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.2.2-1
- kata-containers-2.2.2

* Mon Sep 27 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.2.1-1
- kata-containers-2.2.1

* Fri Sep 17 2021 Jakob Naucke <jakob.naucke@ibm.com> - 2.2.0-3
- Add an s390x build target

* Thu Sep 02 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.2.0-2
- Provide vendored code as a tarball instead of patch

* Wed Sep 01 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.2.0-1
- kata-containers-2.2.0

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.0-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Thu May 27 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.1.0-2
- Add the CRI-O drop-in file to the package
  Resolves: rhbz#1967594
- qemu: Update QEMU binary & its location
  Resolves: rhbz#1967602

* Thu May 27 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.1.0-1
- kata-containers 2.1.0

* Fri Apr 09 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.0.3-1
- kata-containers 2.0.3

* Tue Apr 06 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.0.2-1
- kata-containers 2.0.2

* Mon Mar 08 2021 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.0.1-1
- Kata-containers 2.0.1

* Thu Dec 17 2020 Eduardo Lima (Etrunko) <etrunko@redhat.com> - 2.0.0-1
- Adjust package for Fedora review.

* Thu Nov 26 2020 Fabiano FidĂȘncio <fabiano@fidencio.org> - 2.0.0-0
- Initial packaging
