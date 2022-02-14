Vendor:         Microsoft Corporation
Distribution:   Mariner
Name:           python-charset-normalizer
Version:        2.0.11
Release:        1%{?dist}
Summary:        The Real First Universal Charset Detector

License:        MIT
URL:            https://github.com/ousret/charset_normalizer
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3dist(pytest)


%description
A library that helps you read text from an unknown charset encoding.
Motivated by chardet, trying to resolve the issue by taking
a new approach. All IANA character set names for which the Python core
library provides codecs are supported.

%package -n     python3-charset-normalizer
Summary:        %{summary}

%description -n python3-charset-normalizer
A library that helps you read text from an unknown charset encoding.
Motivated by chardet, trying to resolve the issue by taking
a new approach. All IANA character set names for which the Python core
library provides codecs are supported.

%prep
%autosetup -n charset_normalizer-%{version}
# Remove pytest-cov settings from setup.cfg
sed -i "/addopts = --cov/d" setup.cfg

%generate_buildrequires
%pyproject_buildrequires -r

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files charset_normalizer

%check
%pytest

%files -n python3-charset-normalizer -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/normalizer

%changelog
* Mon Jan 31 2022 Lumír Balhar <lbalhar@redhat.com> - 2.0.11-1
- Update to 2.0.11
Resolves: rhbz#2048279

* Fri Jan 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Wed Jan 05 2022 Lumír Balhar <lbalhar@redhat.com> - 2.0.10-1
- Update to 2.0.10
Resolves: rhbz#2037079

* Fri Dec 17 2021 Lumír Balhar <lbalhar@redhat.com> - 2.0.9-1
- Update to 2.0.9
Resolves: rhbz#2028947

* Mon Nov 29 2021 Lumír Balhar <lbalhar@redhat.com> - 2.0.8-1
- Update to 2.0.8
Resolves: rhbz#2026482

* Thu Oct 14 2021 Lumír Balhar <lbalhar@redhat.com> - 2.0.7-1
- Update to 2.0.7
Resolves: rhbz#2013031

* Mon Sep 20 2021 Lumír Balhar <lbalhar@redhat.com> - 2.0.6-1
- Update to 2.0.6
Resolves: rhbz#2004262

* Mon Aug 02 2021 Lumír Balhar <lbalhar@redhat.com> - 2.0.4-1
- Update to 2.0.4
Resolves: rhbz#1988575

* Wed Jul 21 2021 Lumír Balhar <lbalhar@redhat.com> - 2.0.3-1
- Initial package
