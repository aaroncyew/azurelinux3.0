%global pypi_name sphinxcontrib-htmlhelp

Summary:        Sphinx extension for HTML help files
Name:           python-%{pypi_name}
Version:        2.0.0
Release:        4%{?dist}
License:        BSD
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            http://sphinx-doc.org/
Source0:        %{pypi_source}

BuildArch:      noarch

BuildRequires:  gettext
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools

%if %{with_check}
BuildRequires:  python%{python3_pkgversion}-html5lib
BuildRequires:  python%{python3_pkgversion}-pip
BuildRequires:  python%{python3_pkgversion}-pytest
%endif

%description
sphinxcontrib-htmlhelp is a sphinx extension which renders HTML help files.

%package -n     python%{python3_pkgversion}-%{pypi_name}
%{?python_provide:%python_provide python%{python3_pkgversion}-%{pypi_name}}
Summary:        %{summary}

%description -n python%{python3_pkgversion}-%{pypi_name}
sphinxcontrib-htmlhelp is a sphinx extension which renders HTML help files.

%prep
%autosetup -n %{pypi_name}-%{version}
find -name '*.mo' -delete

%build
for po in $(find -name '*.po'); do
  msgfmt --output-file=${po%.po}.mo ${po}
done
%py3_build

%install
%py3_install

# Move language files to /usr/share
pushd %{buildroot}%{python3_sitelib}
for lang in `find sphinxcontrib/htmlhelp/locales -maxdepth 1 -mindepth 1 -type d -not -path '*/\.*' -printf "%{f} "`;
do
  test $lang == __pycache__ && continue
  install -d %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES
  mv sphinxcontrib/htmlhelp/locales/$lang/LC_MESSAGES/*.mo %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES/
done
rm -rf sphinxcontrib/htmlhelp/locales
ln -s %{_datadir}/locale sphinxcontrib/htmlhelp/locales
popd

%find_lang sphinxcontrib.htmlhelp

%check
pip3 install Sphinx
python3 -m pytest

%files -n python%{python3_pkgversion}-%{pypi_name} -f sphinxcontrib.htmlhelp.lang
%license LICENSE
%doc README.rst
%{python3_sitelib}/sphinxcontrib/
%{python3_sitelib}/sphinxcontrib_htmlhelp-%{version}-py%{python3_version}-*.pth
%{python3_sitelib}/sphinxcontrib_htmlhelp-%{version}-py%{python3_version}.egg-info/

%changelog
* Fri Apr 08 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0.0-4
- Initial CBL-Mariner import from Fedora 36 (license: MIT).
- Cleaning-up spec. License verified.

* Fri Jan 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Fri Jul 23 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri Jun 11 2021 Karolina Surma <ksurma@redhat.com> - 2.0.0-1
- Update to 2.0.0
Resolves: rhbz#1963358

* Thu Jun 03 2021 Python Maint <python-maint@redhat.com> - 1.0.3-5
- Rebuilt for Python 3.10

* Wed Jun 02 2021 Python Maint <python-maint@redhat.com> - 1.0.3-4
- Bootstrap for Python 3.10

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Thu Jun 04 2020 Charalampos Stratakis <cstratak@redhat.com> - 1.0.3-1
- Update to 1.0.3 (#1699073)

* Sat May 23 2020 Miro Hrončok <mhroncok@redhat.com> - 1.0.1-8
- Rebuilt for Python 3.9

* Fri May 22 2020 Miro Hrončok <mhroncok@redhat.com> - 1.0.1-7
- Bootstrap for Python 3.9

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 1.0.1-5
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Fri Aug 16 2019 Miro Hrončok <mhroncok@redhat.com> - 1.0.1-4
- Rebuilt for Python 3.8

* Thu Aug 15 2019 Miro Hrončok <mhroncok@redhat.com> - 1.0.1-3
- Bootstrap for Python 3.8

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Mar 01 2019 Miro Hrončok <mhroncok@redhat.com> - 1.0.1-1
- Initial package
