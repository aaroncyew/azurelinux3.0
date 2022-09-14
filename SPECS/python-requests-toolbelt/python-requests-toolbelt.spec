%global srcname requests-toolbelt
%global altname requests_toolbelt

Summary:        Utility belt for advanced users of python-requests
Name:           python-%{srcname}
Version:        0.9.1
Release:        13%{?dist}
License:        ASL 2.0
URL:            https://toolbelt.readthedocs.io
Source0:        https://github.com/requests/toolbelt/archive/refs/tags/%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
# present in upstream master but not in a stable release yet
Patch0:         python-requests-toolbelt-fix-unhandled-exception-from-tests.patch
# upstream PR 261, currently the upstream tests are broken as some network
# resources vanished
Patch1:         python-requests-toolbelt-pass-session-into-tests.patch
BuildArch:      noarch

%global _description \
This is just a collection of utilities for python-requests, but don’t really\
belong in requests proper.

%description %{_description}

%package -n python3-%{srcname}
Summary:        %{summary}
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
%if %{with_check}
BuildRequires:  python3-pip
BuildRequires:  python3-pytest
%endif
Requires:       python3-requests

%description -n python3-%{srcname} %{_description}

%{?python_provide:%python_provide python3-%{srcname}}
%{?python_provide:%python_provide python3-%{altname}}

%prep
%autosetup -p1 -n toolbelt-%{version}

%build
%py3_build

%install
%py3_install

%check
%{python3} -m pip install atomicwrites attrs docutils pluggy pygments six more-itertools
%{python3} -m pip install mock pyopenssl betamax ndg-httpsclient
%pytest -v --ignore=tests/test_x509_adapter.py tests

%files -n python3-%{srcname}
%license LICENSE
%doc README.rst HISTORY.rst
%{python3_sitelib}/%{altname}/
%{python3_sitelib}/%{altname}-*.egg-info/

%changelog
* Wed Sep 14 2022 Sumedh Sharma <sumsharma@microsoft.com> - 0.9.1-13
- Move from SPECS-EXTENDED to SPECS
- License verified
* Wed Dec 09 2020 Steve Laughman <steve.laughman@microsoft.com> - 0.9.1-12
- Initial CBL-Mariner import from Fedora 33 (license: MIT)
* Sun Oct 18 2020 Parag Nemade <pnemade AT redhat DOT com> - 0.9.1-11
- Ignore failing tests (rh#1863713)
* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-10
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild
* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild
* Mon May 25 2020 Miro Hrončok <mhroncok@redhat.com> - 0.9.1-8
- Rebuilt for Python 3.9
* Sat Apr 11 2020 Felix Schwarz <fschwarz@fedoraproject.org> - 0.9.1-7
- run test suite in %%check
* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild
* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 0.9.1-5
- Rebuilt for Python 3.8.0rc1 (#1748018)
* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 0.9.1-4
- Rebuilt for Python 3.8
* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild
* Thu Apr 04 2019 Parag Nemade <pnemade AT redhat DOT com> - 0.9.1-2
- Remove python2 subpackage (#1696338)
* Thu Jan 31 2019 Parag Nemade <pnemade AT redhat DOT com> - 0.9.1-1
- Update to 0.9.1 version (#1670521)
* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild
* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 0.8.0-4
- Rebuilt for Python 3.7
* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild
* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild
* Sun May 21 2017 Parag Nemade <pnemade AT redhat DOT com> - 0.8.0-1
- Update to 0.8.0 version
* Mon Mar 20 2017 Parag Nemade <pnemade AT redhat DOT com> - 0.7.1-1
- Update to 0.7.1 version
* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.7.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild
* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 0.7.0-2
- Rebuild for Python 3.6
* Sun Jul 24 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.7.0-1
- Update to 0.7.0 (RHBZ #1359456)
* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.2-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages
* Wed Jun 29 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.6.2-1
- Update to 0.6.2
- Add proper python2 subpackage
- Run tests properly
- Other fixes
* Mon May 09 2016 Parag Nemade <pnemade AT redhat DOT com> - 0.6.1-1
- update to 0.6.1 release
* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild
* Thu Jan 28 2016 Parag Nemade <pnemade AT redhat DOT com> - 0.6.0-1
- update to 0.6.0 release
* Mon Dec 21 2015 Parag Nemade <pnemade AT redhat DOT com> - 0.5.1-1
- update to 0.5.1 release
* Thu Nov 26 2015 Parag Nemade <pnemade AT redhat DOT com> - 0.5.0-1
- update to 0.5.0 release
* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5
* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild
* Mon Apr 06 2015 Parag Nemade <pnemade AT redhat DOT com> - 0.4.0-1
- update to 0.4.0 release
* Fri Feb 13 2015 Parag Nemade <pnemade AT redhat DOT com> - 0.3.1-2
- Add missing LICENSE file
* Mon Feb 02 2015 Parag Nemade <pnemade AT redhat DOT com> - 0.3.1-1
- Initial packaging
