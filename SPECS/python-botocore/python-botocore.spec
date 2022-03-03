Summary:        Amazon Web Services Library.
Name:           python-botocore
Version:        1.23.52
Release:        2%{?dist}
License:        ASL 2.0
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Development/Languages/Python
URL:            https://github.com/boto/botocore
#Source0:       https://github.com/boto/botocore/archive/refs/tags/%{version}.tar.gz
Source0:        botocore-%{version}.tar.gz
BuildArch:      noarch

%description
A low-level interface to a growing number of Amazon Web Services. The botocore package is the foundation for the AWS CLI as well as boto3.

%package -n     python3-botocore
Summary:        python3-botocore
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-xml
Requires:       python3
%if %{with_check}
BuildRequires:  python3-pip
%endif

%description -n python3-botocore
A low-level interface to a growing number of Amazon Web Services. The botocore package is the foundation for the AWS CLI as well as boto3.

%prep
%autosetup -n botocore-%{version}

%build
%py3_build

%install
%py3_install

%check
pip3 install tox
tox -e py39

%files -n python3-botocore
%defattr(-,root,root)
%license LICENSE.txt
%{python3_sitelib}/*

%changelog
* Thu Mar 03 2022 Muhammad Falak <mwani@microsfot.com> - 1.23.52-2
- Drop un-needed BRs for `%check` section.
- Switch to tox for testing.

* Wed Feb 09 2022 Nick Samson <nisamson@microsoft.com> - 1.23.52-1
- Upgraded to 1.23.52, updated Source0 URL

* Wed Oct 20 2021 Thomas Crain <thcrain@microsoft.com> - 1.13.21-3
- Add license to python3 package, fix license tag
- Remove python2 package
- Lint spec

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 1.13.21-2
- Added %%license line automatically

* Wed Mar 18 2020 Henry Beberman <henry.beberman@microsoft.com> - 1.13.21-1
- Update to 1.13.21. License verified.

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> - 1.12.0-3
- Initial CBL-Mariner import from Photon (license: Apache2).

* Mon Jan 14 2019 Tapas Kundu <tkundu@vmware.com> - 1.12.0-2
- Fix make check

* Sun Sep 09 2018 Tapas Kundu <tkundu@vmware.com> - 1.12.0-1
- Update to version 1.12.0

* Sun Jan 07 2018 Kumar Kaushik <kaushikk@vmware.com> - 1.8.15-1
- Initial packaging for photon.
