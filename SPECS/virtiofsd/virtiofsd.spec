Vendor:         Microsoft Corporation
Distribution:   Mariner
#
# spec file for package virtiofsd
#
# Copyright (c) 2024 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           virtiofsd
Version:        1.10.1
Release:        2%{?dist}
Summary:        vhost-user virtio-fs device backend written in Rust
Group:          Development/Libraries/Rust
License:        Apache-2.0
URL:            https://gitlab.com/virtio-fs/virtiofsd
Source0:        https://gitlab.com/virtio-fs/virtiofsd/-/archive/v%{version}/%{name}-v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-cargo.tar.gz
Source2:        cargo_config
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  libcap-ng-devel
BuildRequires:  libseccomp-devel
Conflicts:      qemu-tools < 8

%description
vhost-user virtio-fs device backend written in Rust

%prep
%autosetup -n %{name}-v%{version}
#pushd %{name}-v%{version}
tar -xf %{SOURCE1}
install -D %{SOURCE2} .cargo/config
#popd

%build
#pushd %{name}-v%{version}
cargo build --release
#popd

%install
mkdir -p %{buildroot}%{_libexecdir}
install -D -p -m 0755 %{_builddir}/%{name}-%{version}/target/release/virtiofsd %{buildroot}%{_libexecdir}/virtiofsd
install -D -p -m 0644 %{_builddir}/%{name}-%{version}/50-virtiofsd.json %{buildroot}%{_datadir}/qemu/vhost-user/50-virtiofsd.json

%check
cargo test --release

%files
%doc README.md
%{_libexecdir}/virtiofsd
%dir %{_datadir}/qemu
%dir %{_datadir}/qemu/vhost-user
%{_datadir}/qemu/vhost-user/50-virtiofsd.json

%changelog
* Wed Feb 07 2024 Kanika Nema <kanikanema@microsoft.com> - 1.10.1-2
- Initial CBL-Mariner import from openSuse Tumbleweed (license: Apache-2.0)
- License verified
- Remove build dependencies on cargo-packaging

* Tue Jan 30 2024 caleb.crane@suse.com
- Fix CVE-2023-50711: vmm-sys-util: out of bounds memory accesses (bsc#1218502, bsc#1218500)
- Update to version 1.10.1:
  * Bump version to v1.10.1
  * Fix mandatory user namespaces
  * Don't drop supplemental groups in unprivileged user namespace
  * Bump version to v1.10.0
  * Update rust-vmm dependencies (bsc#1218500)
  * Bump version to v1.9.0
- Spec: switch to using the upstream virtio-fs config file for qemu
- Spec: switch back to greedy cargo updates of vendored dependencies
* Thu Aug 31 2023 Caleb Crane <caleb.crane@suse.com>
- Update to upstream version v1.7.2 (jsc#4980)
  - Add supplementary group extension support
  - Prevent EPERM failures with O_NOATIME
  - Fix cache timeouts
  - seccomp: Allow SYS_sched_yield
  - Allow to provide the same argument multiple times
  - Add the -V/--version options
- Upgrade vendored dependencies
* Fri Jun  2 2023 Caleb Crane <caleb.crane@suse.com>
- Add qemu config file to ensure qemu is aware of the virtiofsd executable
- https://www.reddit.com/r/suse/comments/13xmote/vm_with_virtiofs_does_not_start_unable_to_find_a/
* Thu May 25 2023 Caleb Crane <caleb.crane@suse.com>
- Remove exclusive arch, only disable for 32-bit archs (i586 and armv7l)
- Add package conflict with the previous implementation of virtiofsd inside
  older versions of the qemu-tools package (qemu-tools < 8)
* Tue May 23 2023 Caleb Crane <caleb.crane@suse.com>
- Initial release of virtiofsd v1.6.1
