# Generated by go2rpm
%bcond_without check

Name:           vitess
Version:        19.0.4
Release:        1%{?dist}
Summary:        Database clustering system for horizontal scaling of MySQL
# Upstream license specification: MIT and Apache-2.0
License:        MIT and ASL 2.0
Vendor:         Microsoft Corporation
Distribution:   Azure Linux
URL:            https://github.com/vitessio/vitess
#Source0:       https://github.com/vitessio/%{name}/archive/refs/tags/v%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz
# Below is a manually created tarball, no download link.
# We're using pre-populated Go modules from this tarball, since network is disabled during build time.
# How to re-build this file:
#   1. wget https://github.com/vitessio/vitess/archive/refs/tags/%%{version}.tar.gz -O %%{name}-%%{version}.tar.gz
#   2. tar -xf %%{name}-%%{version}.tar.gz
#   3. cd %%{name}-%%{version}
#   4. go mod vendor
#   5. tar  --sort=name \
#           --mtime="2021-04-26 00:00Z" \
#           --owner=0 --group=0 --numeric-owner \
#           --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
#           -cf %%{name}-%%{version}-vendor.tar.gz vendor
#
Source1:        %{name}-%{version}-vendor.tar.gz 
BuildRequires: golang

%description
Vitess is a database clustering system for horizontal scaling of MySQL through
generalized sharding.

By encapsulating shard-routing logic, Vitess allows application code and
database queries to remain agnostic to the distribution of data onto multiple
shards. With Vitess, you can even split and merge shards as your needs grow,
with an atomic cutover step that takes only a few seconds.


%prep
%autosetup -p1

# sed in Mariner does not work on a group of files; use for-loop to apply
# to apply to individual file
for i in $(find . -iname "*.go" -type f); do
  sed -i "s|github.com/coreos/etcd|go.etcd.io/etcd|" $i
  sed -i "s|gotest.tools|gotest.tools/v3|" $i
done

rm -rf go/trace/plugin_datadog.go
mv go/README.md README-go.md

%build

# create vendor folder from the vendor tarball and set vendor mode
tar -xf %{SOURCE1} --no-same-owner

export VERSION=%{version}

for cmd in $(find go/cmd/* -maxdepth 0 -type d); do
  # Skip internal directory
  if [ "$cmd" == "go/cmd/internal" ]; then
    continue
  fi
  go build -buildmode pie -compiler gc '-tags=rpm_crashtraceback ' \
           -ldflags "-X vitess.io/vitess/version=$VERSION -extldflags -Wl,-z,relro" \
           -mod=vendor -v -a -x -o ./bin/$(basename $cmd) ./$cmd
done

%install
install -m 0755 -vd                     %{buildroot}%{_bindir}
install -m 0755 -vp ./bin/*             %{buildroot}%{_bindir}/

%check
go check -t go/cmd \
         -d go/mysql \
         -d go/mysql/endtoend \
         -d go/sqltypes \
         -d go/vt/hook \
         -d go/vt/mysqlctl \
         -d go/vt/srvtopo \
         -t go/vt/topo \
         -d go/vt/vtctld \
         -d go/vt/vtgate/evalengine \
         -d go/vt/vtqueryserver \
         -d go/vt/vttablet/endtoend \
         -t go/vt/vttablet/tabletmanager \
         -t go/vt/vttablet/tabletserver \
         -t go/vt/vttablet/worker \
         -d go/vt/withddl \
         -t go/vt/worker \
         -d go/vt/workflow/reshardingworkflowgen \
         -d go/vt/wrangler \
         -d go/vt/wrangler/testlib \
         -d go/vt/zkctl \
         -d go/json2 \
         -t go/test/endtoend

%files
%license LICENSE
%doc CODE_OF_CONDUCT.md GOVERNANCE.md GUIDING_PRINCIPLES.md
%doc ADOPTERS.md CONTRIBUTING.md README.md README-go.md
%{_bindir}/*

%changelog
* Tue Jun 25 2024 Nicolas Guibourge <nicolasg@microsoft.com> - 19.0.4-1
- Auto-upgrade to 17.0.2 - Azure Linux 3.0 - package upgrades

* Fri Oct 27 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 17.0.2-1
- Auto-upgrade to 17.0.2 - Azure Linux 3.0 - package upgrades

* Mon Oct 16 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 16.0.2-6
- Bump release to rebuild with go 1.20.10

* Tue Oct 10 2023 Dan Streetman <ddstreet@ieee.org> - 16.0.2-5
- Bump release to rebuild with updated version of Go.

* Mon Aug 07 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 16.0.2-4
- Bump release to rebuild with go 1.19.12

* Thu Jul 13 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 16.0.2-3
- Bump release to rebuild with go 1.19.11

* Thu Jun 15 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 16.0.2-2
- Bump release to rebuild with go 1.19.10

* Fri May 12 2023 Bala <balakumaran.kannan@microsoft.com> - 16.0.2-1
- Update to 16.0.2 to fix CVE-2023-29194
- Remove all the patches are they are merged with latest version

* Wed Apr 05 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 8.0.0-12
- Bump release to rebuild with go 1.19.8

* Tue Mar 28 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 8.0.0-11
- Bump release to rebuild with go 1.19.7

* Wed Mar 15 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 8.0.0-10
- Bump release to rebuild with go 1.19.6

* Fri Feb 03 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 8.0.0-9
- Bump release to rebuild with go 1.19.5

* Wed Jan 18 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 8.0.0-8
- Bump release to rebuild with go 1.19.4

* Fri Dec 16 2022 Daniel McIlvaney <damcilva@microsoft.com> - 8.0.0-7
- Bump release to rebuild with go 1.18.8 with patch for CVE-2022-41717

* Tue Nov 01 2022 Olivia Crain <oliviacrain@microsoft.com> - 8.0.0-6
- Bump release to rebuild with go 1.18.8

* Mon Aug 22 2022 Olivia Crain <oliviacrain@microsoft.com> - 8.0.0-5
- Bump release to rebuild against Go 1.18.5

* Tue Jun 14 2022 Muhammad Falak <mwani@microsoft.com> - 8.0.0-4
- Bump release to rebuild with golang 1.18.3

* Mon Aug 16 2021 Henry Li <lihl@microsoft.com> - 8.0.0-3
- Initial CBL-Mariner import from Fedora 34 (license: MIT)
- License Verified
- Use golang as BR
- Use prebuilt vendor source for building
- Remove unsupported macros in Mariner
- Use for loop to apply sed changes
- Apply patch to use new versions to dependent golang modules

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 8.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sat Dec 26 13:28:45 CET 2020 Robert-André Mauchin <zebob.m@gmail.com> - 8.0.0-1
- Update to 8.0.0
- Close: rhbz#1742264

* Thu Oct 01 11:57:17 CEST 2020 Robert-André Mauchin <zebob.m@gmail.com> - 7.0.2-1
- Update to 7.0.2

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 5.0.1-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 5.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Apr 08 2020 Robert-André Mauchin <zebob.m@gmail.com> - 5.0.1-1
- Update to 5.0.1

* Mon Feb 17 2020 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 3.0-4
- Rebuilt for GHSA-jf24-p9p9-4rjh

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu May 16 00:30:49 CEST 2019 Robert-André Mauchin <zebob.m@gmail.com> - 3.0-1.20190701git948c251
- Initial package
