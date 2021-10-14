Name: patterns-ceph-containers
Version: 1.0
Release: bp153.1.5
Summary: Patterns for the Ceph containers
License: MIT
Vendor:  Microsoft Corporation
Distribution: Mariner
Group: Metapackages
Url: http://en.opensuse.org/Patterns
Source0: %{name}-rpmlintrc
ExclusiveArch: x86_64 aarch64 ppc64le s390x

%description
This is an internal package that is used to create the patterns as part
of the installation source setup. Installation of this package does
not make sense.

%package ceph_base
Summary: Ceph base
Group: Metapackages
Provides: pattern() = ceph_base
#Provides: pattern-icon() = yast-iscsi-client
Provides: pattern-category() = Containers
Provides: pattern-order() = 3000
Provides: pattern-visible()
Requires: ceph
Requires: ceph-base
Requires: ceph-common
Requires: ceph-fuse
Requires: cephadm
Requires: ceph-grafana-dashboards
Requires: ceph-mds
Requires: ceph-mgr
Requires: ceph-mgr-rook
Requires: ceph-mgr-cephadm
Requires: ceph-mgr-dashboard
#Temporarily commenting out dependency to allow package to build
#Requires: ceph-mgr-diskprediction-local
Requires: ceph-mon
Requires: ceph-osd
Requires: ceph-prometheus-alerts
Requires: ceph-radosgw
#Temporarily commenting out dependency to allow package to build
#Requires: ceph-iscsi
Requires: rbd-mirror
Requires: rbd-nbd
Requires: ca-certificates
Requires: e2fsprogs
Requires: kmod
Requires: lvm2
Requires: gptfdisk

%description ceph_base
This provides the base for the Ceph, Rook, Ceph CSI driver packages and containers.

%prep
# empty on purpose

%build
# empty on purpose

%install
mkdir -p %buildroot/usr/share/doc/packages/patterns-ceph-containers/
echo 'This file marks the pattern ceph-base to be installed.' >%buildroot/usr/share/doc/packages/patterns-ceph-containers/ceph_base.txt

%files ceph_base
%defattr(-,root,root)
%dir %{_docdir}/packages/patterns-ceph-containers
%{_docdir}/packages/patterns-ceph-containers/ceph_base.txt

%changelog
* Mon Oct 4 2021 Max Brodeur-Urbas <maxbr@microsoft.com> - 1.0-1
- Initial CBL-Mariner import from OpenSuse (license: MIT)
- License Verified
- Modified installation path 
* Mon Feb  1 2021 Nathan Cutler <ncutler@suse.com>
- Drop all nfs-ganesha packages from ceph-base:
  + nfs-ganesha
  + nfs-ganesha-ceph
  + nfs-ganesha-rgw
  + nfs-ganesha-rados-grace
  + nfs-ganesha-rados-urls
* Tue Jan 28 2020 Denis Kondratenko <denis.kondratenko@suse.com>
- Added nfs-ganesha-rados-urls to ceph_base
* Fri Dec 13 2019 Kristoffer Gronlund <kgronlund@suse.com>
- ceph-daemon was renamed to cephadm
- ceph-mgr-ssh was renamed to ceph-mgr-cephadm
* Thu Nov 28 2019 Kristoffer Gronlund <kgronlund@suse.com>
- Add missing dependencies to pattern
* Mon Jul 22 2019 Denis Kondratenko <denis.kondratenko@suse.com>
- Rename pattern according to the recomendations (replacing "-" with "_")
* Mon Jul 22 2019 Denis Kondratenko <denis.kondratenko@suse.com>
- Add missing packages (mgr) to the pattern
* Wed Jul 17 2019 Denis Kondratenko <denis.kondratenko@suse.com>
- Initial version