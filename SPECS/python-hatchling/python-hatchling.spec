# Disable tests as it requires new package python-exceptiongroup
%global with_check 0
%global srcname hatchling
Vendor:         Microsoft Corporation
Distribution:   Azure Linux

%undefine mariner_module_ldflags

## START: Set by rpmautospec
## (rpmautospec version 0.5.1)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 2;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

Name:           python-%{srcname}
Version:        1.21.1
Release:        %autorelease
Summary:        The build backend used by Hatch

# SPDX
License:        MIT
URL:            https://pypi.org/project/%{srcname}
Source0:        %{pypi_source %{srcname}}
# Written for Fedora in groff_man(7) format based on --help output
Source100:      hatchling.1
Source200:      hatchling-build.1
Source300:      hatchling-dep.1
Source310:      hatchling-dep-synced.1
Source400:      hatchling-metadata.1
Source500:      hatchling-version.1

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-six
BuildRequires:  python3-wheel
BuildRequires:  python3-pathspec
BuildRequires:  python3-pluggy
BuildRequires:  python3-tomli
BuildRequires:  python3-packaging
BuildRequires:  python3-pyparsing
BuildRequires:  python3-trove-classifiers
BuildRequires:  python3-pytest

%global common_description %{expand:
This is the extensible, standards compliant build backend used by Hatch.}

%description %{common_description}


%package -n python3-%{srcname}
Summary:        %{summary}

%description -n python3-%{srcname} %{common_description}


%prep
%autosetup -n %{srcname}-%{version}


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files %{srcname}

install -t '%{buildroot}%{_mandir}/man1' -D -p -m 0644 \
    '%{SOURCE100}' \
    '%{SOURCE200}' \
    '%{SOURCE300}' '%{SOURCE310}' \
    '%{SOURCE400}' \
    '%{SOURCE500}'


%check
%if %{with_check}
%pytest
%endif


%files -n python3-%{srcname} -f %{pyproject_files}
%license %{python3_sitearch}/%{srcname}-%{version}.dist-info/licenses/LICENSE.txt
%doc README.md

%{_bindir}/hatchling
%{_mandir}/man1/hatchling.1*
%{_mandir}/man1/hatchling-*.1*


%changelog
* Mon Feb 26 2024 Bala <balakumaran.kannan@microsoft.com> - 1.21.1-2
- Initial CBL-Mariner import from Fedora 39 (license: MIT)
- License verified.

## START: Generated by rpmautospec
* Thu Jan 25 2024 Benjamin A. Beasley <code@musicinmybrain.net> - 1.21.1-1
- Update to 1.21.1 (close RHBZ#2260286)

* Wed Dec 20 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.21.0-1
- Update to 1.21.0 (close RHBZ#2254951)

* Wed Dec 13 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.20.0-1
- Update to 1.20.0 (close RHBZ#2253944)

* Fri Jul 21 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.18.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Sat Jul 01 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.18.0-1
- Update to 1.18.0 (close RHBZ#2214286)

* Tue Jun 13 2023 Python Maint <python-maint@redhat.com> - 1.17.1-2
- Rebuilt for Python 3.12

* Mon Jun 05 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.17.1-1
- Update to 1.17.1 (close RHBZ#2212081)

* Fri May 12 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.17.0-1
- Update to 1.17.0 (close RHBZ#2203351)

* Fri May 12 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.16.1-2
- Drop lower-bound on pyproject-rpm-macros

* Thu May 11 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.16.1-1
- Update to 1.16.1 (close RHBZ#2203227)

* Thu May 11 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.16.0-1
- Update to 1.16 (close RHBZ#2196940)

* Wed May 10 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.15.0-1
- Update to 1.15.0 (close RHBZ#2196648)

* Tue Apr 25 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.1-1
- Update to 1.14.1 (close RHBZ#2188977)

* Mon Apr 03 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.14.0-1
- Update to 1.14.0 (close RHBZ#21838751)

* Thu Feb 09 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.13.0-1
- Update to 1.13.0 (close RHBZ#2168481)

* Fri Jan 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Thu Jan 05 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.12.2-1
- Update to 1.12.2 (close RHBZ#2158329)

* Sat Dec 31 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.12.1-1
- Update to 1.12.1 (close RHBZ#2157116)

* Wed Oct 19 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.11.1-1
- Update to 1.11.1 (close RHBZ#2136026)

* Sun Oct 09 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.11.0-1
- Update to 1.11.0 (close RHBZ#2133226)
- Improve the man pages

* Mon Sep 19 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.10.0-1
- Update to 1.10.0 (close RHBZ#2127792)

* Sat Sep 10 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.9.0-1
- Update to 1.9.0 (close RHBZ#2125746)
- Use new “prepare_metadata_…” hooks for BuildRequires

* Thu Aug 25 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.8.1-1
- Update to 1.8.1 (close RHBZ#2121312)

* Tue Aug 16 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.8.0-1
- Update to 1.8.0 (close RHBZ#2117979)

* Sun Jul 24 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.6.0-1
- Update to 1.6.0 (close RHBZ#2110167)

* Fri Jul 22 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Mon Jul 11 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.5.0-1
- Update to 1.5.0 (close RHBZ#2105880)

* Thu Jul 07 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.4.1-1
- Update to 1.4.1 (close RHBZ#2103496)

* Mon Jun 13 2022 Python Maint <python-maint@redhat.com> - 1.3.1-2
- Rebuilt for Python 3.11

* Mon May 30 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.3.1-1
- Update to 1.3.1 (close RHBZ#1609549)

* Mon May 23 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.3.0-1
- Update to 1.3.0 (close RHBZ#2089077)

* Sat May 21 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.2.0-1
- Update to 1.2.0 (close RHBZ#2088843)

* Fri May 20 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.1.0-1
- Update to 1.1.0 (close RHBZ#2088671)

* Wed May 18 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.0.0-1
- Update to 1.0.0 (close RHBZ#2087533)

* Mon May 16 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.25.0-1
- Update to 0.25.0 (close RHBZ#2086373)

* Fri May 06 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.24.0-2
- Use wheel-building support to generate BR’s

* Sat Apr 30 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.24.0-1
- Update to 0.24.0 (close RHBZ#2079689)

* Tue Apr 12 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.22.0-2
- Adjust for pyproject-rpm-macros >= 1.1.0

* Sun Mar 27 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.22.0-1
- Update to 0.22.0 (close RHBZ#2068853)

* Tue Mar 22 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.21.1-1
- Update to 0.21.1 (close RHBZ#2066578)

* Fri Mar 18 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.21.0-1
- Update to 0.21.0 (close RHBZ#2065524)

* Mon Mar 07 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.20.1-1
- Update to 0.20.1 (close RHBZ#2061214)

* Mon Feb 28 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.18.0-1
- Update to 0.18.0 (close RHBZ#2059065)

* Sun Feb 27 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.17.0-1
- Update to 0.17.0 (close RHBZ#2058939)

* Sat Feb 26 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.16.0-1
- Update to 0.16.0 (close RHBZ#2058884)

* Wed Feb 23 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.15.0-1
- Update to 0.15.0 (close RHBZ#2057315)

* Sun Feb 20 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.14.0-1
- Update to 0.14.0 (close RHBZ#2050889)

* Sun Feb 20 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.11.3-3
- Simplify man page installation

* Sun Feb 20 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.11.3-2
- Clarify man page hand-written status

* Sun Feb 20 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 0.11.3-1
- Initial package
## END: Generated by rpmautospec
