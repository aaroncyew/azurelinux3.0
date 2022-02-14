Vendor:         Microsoft Corporation
Distribution:   Mariner
%global pypi_name tox-current-env
%global pypi_under tox_current_env

Name:           python-%{pypi_name}
Version:        0.0.7
Release:        2%{?dist}
Summary:        Tox plugin to run tests in current Python environment

License:        MIT
URL:            https://github.com/fedora-python/tox-current-env
Source0:        %{pypi_source}
BuildArch:      noarch

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  pyproject-rpm-macros

%description
The tox-current-env plugin allows to run tests in current Python environment.


%package -n     python%{python3_pkgversion}-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python%{python3_pkgversion}-%{pypi_name}}

%description -n python%{python3_pkgversion}-%{pypi_name}
The tox-current-env plugin allows to run tests in current Python environment.


%prep
%autosetup -n %{pypi_name}-%{version}


%generate_buildrequires
# Don't use %%pyproject_buildrequires -t/-e to avoid a build dependency loop
%pyproject_buildrequires -r


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files %{pypi_under}


%check
# the tests currently only work within actual tox and with various Python
# versions installed, so we skip them and do an import check only instead:
%pyproject_check_import


%files -n python%{python3_pkgversion}-%{pypi_name} -f %{pyproject_files}
%doc README.rst


%changelog
* Mon Feb 14 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 0.0.7-2
- Initial CBL-Mariner import from Fedora 36 (license: MIT).

* Mon Feb 07 2022 Miro Hrončok <mhroncok@redhat.com> - 0.0.7-1
- Update to 0.0.7 to pin tox < 4

* Fri Jan 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Thu Aug 05 2021 Miro Hrončok <mhroncok@redhat.com> - 0.0.6-4
- In %%check, test if the module at least imports

* Tue Jul 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.6-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Wed Jun 02 2021 Python Maint <python-maint@redhat.com> - 0.0.6-2
- Rebuilt for Python 3.10

* Mon Mar 29 2021 Miro Hrončok <mhroncok@redhat.com> - 0.0.6-1
- Update to 0.0.6

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Nov 25 2020 Miro Hrončok <mhroncok@redhat.com> - 0.0.5-1
- Update to 0.0.5

* Wed Nov 04 2020 Miro Hrončok <mhroncok@redhat.com> - 0.0.4-1
- Update to 0.0.4

* Wed Sep 30 2020 Miro Hrončok <mhroncok@redhat.com> - 0.0.3-1
- Update to 0.0.3

* Wed Aug 12 2020 Miro Hrončok <mhroncok@redhat.com> - 0.0.2-7
- Fix FTBFS with pyproject-rpm-macros >= 0-23

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sat May 23 2020 Miro Hrončok <mhroncok@redhat.com> - 0.0.2-5
- Rebuilt for Python 3.9

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 0.0.2-3
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 0.0.2-2
- Rebuilt for Python 3.8

* Mon Aug 12 2019 Miro Hrončok <mhroncok@redhat.com> - 0.0.2-1
- Update to 0.0.2

* Wed Jul 24 2019 Miro Hrončok <mhroncok@redhat.com> - 0.0.1-1
- Initial package
