Vendor:         Microsoft Corporation
Distribution:   Mariner
## START: Set by rpmautospec
## (rpmautospec version 0.2.5)
%define autorelease(e:s:pb:) %{?-p:0.}%{lua:
    release_number = 5;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{?dist}
## END: Set by rpmautospec

# Generated by go2rpm 1.3
%bcond_without check
%global shortname prometheus-node-exporter

# https://github.com/prometheus/node_exporter
%global goipath         github.com/prometheus/node_exporter
Version:                1.3.1

#%gometa

%global common_description %{expand:
Prometheus exporter for hardware and OS metrics exposed by *NIX kernels, written
in Go with pluggable metric collectors.}

%global golicenses      LICENSE NOTICE
%global godocs          docs examples CHANGELOG.md CODE_OF_CONDUCT.md\\\
                        CONTRIBUTING.md MAINTAINERS.md SECURITY.md README.md

Name:           %{goname}
Release:        6%{?dist}
Summary:        Exporter for machine metrics

# Upstream license specification: Apache-2.0
License:        ASL 2.0 and MIT
URL:            %{gourl}
Source0:        https://github.com/prometheus/node_exporter/archive/refs/tags/v%{version}.tar.gz#/%{shortname}-%{version}.tar.gz
Source1:        %{shortname}.sysusers
Source2:        %{shortname}.service
Source3:        %{shortname}.conf
Source4:        %{shortname}.logrotate
# Replace defaults paths for config files
Patch0:         defaults-paths.patch
# https://github.com/prometheus/node_exporter/pull/2190
Patch1:         0001-Refactor-perf-collector.patch

BuildRequires:  go-rpm-macros
BuildRequires:  systemd-rpm-macros
BuildRequires:  golang(github.com/beevik/ntp)
BuildRequires:  golang(github.com/coreos/go-systemd/dbus)
BuildRequires:  golang(github.com/ema/qdisc)
BuildRequires:  golang(github.com/go-kit/log)
BuildRequires:  golang(github.com/go-kit/log/level)
BuildRequires:  golang(github.com/godbus/dbus)
BuildRequires:  golang(github.com/hashicorp/go-envparse)
BuildRequires:  golang(github.com/hodgesds/perf-utils)
BuildRequires:  golang(github.com/jsimonetti/rtnetlink)
BuildRequires:  golang(github.com/mattn/go-xmlrpc)
BuildRequires:  golang(github.com/mdlayher/wifi)
BuildRequires:  golang(github.com/prometheus/client_golang/prometheus)
BuildRequires:  golang(github.com/prometheus/client_golang/prometheus/collectors)
BuildRequires:  golang(github.com/prometheus/client_golang/prometheus/promhttp)
BuildRequires:  golang(github.com/prometheus/client_model/go)
BuildRequires:  golang(github.com/prometheus/common/expfmt)
BuildRequires:  golang(github.com/prometheus/common/promlog)
BuildRequires:  golang(github.com/prometheus/common/promlog/flag)
BuildRequires:  golang(github.com/prometheus/common/version)
BuildRequires:  golang(github.com/prometheus/exporter-toolkit/web)
BuildRequires:  golang(github.com/prometheus/procfs)
BuildRequires:  golang(github.com/prometheus/procfs/bcache)
BuildRequires:  golang(github.com/prometheus/procfs/blockdevice)
BuildRequires:  golang(github.com/prometheus/procfs/btrfs)
BuildRequires:  golang(github.com/prometheus/procfs/nfs)
BuildRequires:  golang(github.com/prometheus/procfs/sysfs)
BuildRequires:  golang(github.com/prometheus/procfs/xfs)
BuildRequires:  golang(github.com/safchain/ethtool)
BuildRequires:  golang(github.com/soundcloud/go-runit/runit)
BuildRequires:  golang(golang.org/x/sys/unix)
BuildRequires:  golang(gopkg.in/alecthomas/kingpin.v2)

%if %{with check}
# Tests
BuildRequires:  golang(github.com/prometheus/client_golang/prometheus/testutil)
%endif

Requires(pre): shadow-utils

%description
%{common_description}

%gopkg

%prep
%goprep
%patch0 -p1
%patch1 -p1

%build
export BUILDTAGS="netgo osusergo static_build"
LDFLAGS="-X github.com/prometheus/common/version.Version=%{version}  \
         -X github.com/prometheus/common/version.Revision=%{release} \
         -X github.com/prometheus/common/version.Branch=tarball      \
         -X github.com/prometheus/common/version.BuildDate=$(date -u -d@$SOURCE_DATE_EPOCH +%%Y%%m%%d)"
%gobuild -o %{gobuilddir}/bin/node_exporter %{goipath}

%install
%gopkginstall
install -m 0755 -vd                     %{buildroot}%{_bindir}
install -m 0755 -vp %{gobuilddir}/bin/* %{buildroot}%{_bindir}/
mv %{buildroot}%{_bindir}/node_exporter %{buildroot}%{_bindir}/%{shortname}
pushd %{buildroot}%{_bindir}
ln -s %{shortname} node_exporter
popd

install -Dpm0644 %{S:1} %{buildroot}%{_sysusersdir}/%{shortname}.conf
install -Dpm0644 %{S:2} %{buildroot}%{_unitdir}/%{shortname}.service
install -Dpm0644 %{S:3} %{buildroot}%{_sysconfdir}/default/%{shortname}
install -Dpm0644 example-rules.yml %{buildroot}%{_datadir}/prometheus/node-exporter/example-rules.yml
install -Dpm0644 %{S:4} %{buildroot}%{_sysconfdir}/logrotate.d/%{shortname}
mkdir -vp %{buildroot}%{_sharedstatedir}/prometheus/node-exporter

# Build man pages.
mkdir -vp %{buildroot}/%{_mandir}/man1/
%{buildroot}%{_bindir}/%{shortname} --help-man > \
    %{buildroot}/%{_mandir}/man1/%{shortname}.1
sed -i '/^  /d; /^.SH "NAME"/,+1c.SH "NAME"\nprometheus-node-exporter \\- The Prometheus Node-Exporter' \
    %{buildroot}/%{_mandir}/man1/%{shortname}.1

%if %{with check}
%check
%gocheck -d collector
%endif

%pre
%sysusers_create_compat %{SOURCE1}

%post
%systemd_post %{shortname}.service

%preun
%systemd_preun %{shortname}.service

%postun
%systemd_postun_with_restart %{shortname}.service

%files
%license LICENSE NOTICE
%doc docs examples CHANGELOG.md CODE_OF_CONDUCT.md CONTRIBUTING.md
%doc MAINTAINERS.md SECURITY.md README.md
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/default/%{shortname}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{shortname}
%{_sysusersdir}/%{shortname}.conf
%{_unitdir}/%{shortname}.service
%{_mandir}/man1/%{shortname}.1*
%{_datadir}/prometheus/node-exporter/example-rules.yml
%dir %attr(0755,prometheus,prometheus) %{_sharedstatedir}/prometheus
%dir %attr(0755,prometheus,prometheus) %{_sharedstatedir}/prometheus/node-exporter

%gopkgfiles

%changelog
* Mon Jan 31 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.3.1-6
- Initial CBL-Mariner import from Fedora 36 (license: MIT).

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> 1.3.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Sun Jan 16 2022 Robert-André Mauchin <zebob.m@gmail.com> 1.3.1-4
- Add logrotate file

* Sat Jan 15 2022 Robert-André Mauchin <zebob.m@gmail.com> 1.3.1-3
- Add LDFLAGS

* Fri Jan 14 2022 Robert-André Mauchin <zebob.m@gmail.com> 1.3.1-2
- Fix home directory permissions

* Fri Jan 14 2022 Robert-André Mauchin <zebob.m@gmail.com> 1.3.1-1
- Update to 1.3.1 Close: rhbz#2024811 Close: rhbz#2039257

* Thu Aug 12 2021 Robert-André Mauchin <zebob.m@gmail.com> 1.2.2-1
- Update to 1.2.2 Close: rhbz#1945422

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Sun Mar 28 18:14:35 CEST 2021 Robert-André Mauchin <zebob.m@gmail.com> - 1.1.1-2
- Fix binary location

* Wed Feb 17 22:48:22 CET 2021 Robert-André Mauchin <zebob.m@gmail.com> - 1.1.1-1
- Initial package

