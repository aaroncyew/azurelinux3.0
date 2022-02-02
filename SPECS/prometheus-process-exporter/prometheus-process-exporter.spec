%global build_date $(date +"%%Y%%m%%d-%%T")
%global debug_package %{nil}
%global go_version %(go version | sed -E 's/go version go(\S+).*/\1/')

Summary:        Prometheus exporter exposing process metrics from procfs
Name:           prometheus-process-exporter
Version:        0.7.10
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://github.com/ncabatoff/process-exporter
Source0:        https://github.com/ncabatoff/process-exporter/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Below is a manually created tarball, no download link.
# We're using vendored Go modules from this tarball, since network is disabled during build time.
# How to re-build this file:
#   1. wget https://github.com/ncabatoff/process-exporter/archive/refs/tags/v%%{version}.tar.gz -O %%{name}-%%{version}.tar.gz
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

BuildRequires:  golang
BuildRequires:  systemd-rpm-macros

Requires(pre):  shadow-utils

%description
Prometheus exporter that exposes process metrics from procfs.

Some apps are impractical to instrument directly, either because you don't
control the code or they're written in a language that isn't easy to
instrument with Prometheus. This exporter solves that issue by mining
process metrics from procfs.

%prep
%autosetup -n process-exporter-%{version} -p1

rm -rf vendor
tar -xf %{SOURCE1} --no-same-owner

%build
LDFLAGS="-X github.com/ncabatoff/process-exporter/version.Version=%{version}      \
         -X github.com/ncabatoff/process-exporter/version.Revision=%{release}     \
         -X github.com/prometheus/common/version.Branch=tarball                   \
         -X github.com/ncabatoff/process-exporter/version.BuildDate=%{build_date} \
         -X github.com/ncabatoff/process-exporter/version.GoVersion=%{go_version}"

# Modified "build" target from Makefile.
CGO_ENABLED=0 go build -ldflags "$LDFLAGS" -mod=vendor -v -a -tags netgo -o process-exporter ./cmd/process-exporter

%install
%make_install
pushd %{buildroot}%{_bindir}
ln -s %{name} process-exporter
popd

%check
make test integ

%files
%license LICENSE
%{_bindir}/*process-exporter

%changelog
* Tue Feb 01 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 0.7.10-1
- Initial CBL-Mariner import from Debian source package (license: MIT).
- License verified.
