Summary:        An implementation of JSON Schema validation for Python
Name:           python-jsonschema
Version:        3.2.0
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Development/Languages/Python
URL:            https://pypi.python.org/pypi/jsonschema
Source0:        https://pypi.python.org/packages/source/j/jsonschema/jsonschema-%{version}.tar.gz
BuildArch:      noarch

%description
jsonschema is JSON Schema validator currently based on
http://tools.ietf.org/html/draft-zyp-json-schema-03

%package -n     python3-jsonschema
Summary:        An implementation of JSON Schema validation for Python
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-vcversioner
BuildRequires:  python3-xml
BuildRequires:  python3-wheel
%if %{with_check}
BuildRequires:  python3-pip
%endif
Requires:       python3

%description -n python3-jsonschema
jsonschema is JSON Schema validator currently based on
http://tools.ietf.org/html/draft-zyp-json-schema-03

%prep
%autosetup -n jsonschema-%{version}

%build
%py3_build

%install
%py3_install
ln -s jsonschema %{buildroot}%{_bindir}/jsonschema3

%check
pip3 install tox
tox -e py39

%files -n python3-jsonschema
%defattr(-,root,root)
%license COPYING
%{python3_sitelib}/*
%{_bindir}/jsonschema
%{_bindir}/jsonschema3

%changelog
* Mon Mar 07 2022 Muhammad Falak <mwani@microsoft.com> - 3.2.0-1
- Bump version to 3.2.0
- Add an explicit BR on `python3-pip` & `python3-wheel`
- Switch to `tox` to enable ptest

* Wed Oct 20 2021 Thomas Crain <thcrain@microsoft.com> - 2.6.0-6
- Remove python2 package
- Lint spec

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 2.6.0-5
- Added %%license line automatically

* Wed May 06 2020 Paul Monson <paulmon@microsoft.com> - 2.6.0-4
- Restore python-vcversioner to enable build without internet access.

* Mon Apr 13 2020 Nicolas Ontiveros <niontive@microsoft.com> - 2.6.0-3
- Don't use python-vcversioner in build.

* Wed Apr 08 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.6.0-2
- Initial CBL-Mariner import from Photon (license: Apache2).
- Switched "Source0" and "URL" tags to use https.
- License verified.

* Tue Oct 23 2018 Sujay G <gsujay@vmware.com> - 2.6.0-1
- Initial version
