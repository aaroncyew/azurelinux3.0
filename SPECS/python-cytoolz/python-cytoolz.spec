%global srcname cytoolz
%define py_setup_args --with-cython
Summary:        Cython implementation of the toolz package
Name:           python-%{srcname}
Version:        0.12.2
Release:        1%{?dist}
License:        BSD
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://github.com/pytoolz/cytoolz/
Source0:        https://files.pythonhosted.org/packages/source/c/cytoolz/%{srcname}-%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
BuildRequires:  gcc

%description
Cython implementation of the toolz package, which provides high performance
utility functions for iterables, functions, and dictionaries.

toolz is a pure Python package that borrows heavily from contemporary
functional languanges. It is designed to interoperate seamlessly with other
libraries including itertools, functools, and third party libraries. High
performance functional data analysis is possible with builtin types like list
and dict, and user-defined data structures; and low memory usage is achieved
by using the iterator protocol and returning iterators whenever possible.

cytoolz implements the same API as toolz. The main differences are that
cytoolz is faster (typically 2-5x faster with a few spectacular exceptions)
and cytoolz offers a C API that is accessible to other projects developed in
Cython. Since toolz is able to process very large (potentially infinite) data
sets, the performance increase gained by using cytoolz can be significant.

See the PyToolz documentation at http://toolz.readthedocs.org.

%package -n python%{python3_pkgversion}-%{srcname}
%{?python_provide:%python_provide python%{python3_pkgversion}-%{srcname}}
Summary:        Cython implementation of the toolz package
BuildRequires:  python%{python3_pkgversion}-Cython
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-toolz >= 0.9.0
Requires:       python%{python3_pkgversion}-toolz >= 0.9.0
%if %{with_check}
BuildRequires:  build-essential
BuildRequires:  python3-pip
%endif

%description -n python%{python3_pkgversion}-%{srcname}
Cython implementation of the toolz package, which provides high performance
utility functions for iterables, functions, and dictionaries.

toolz is a pure Python package that borrows heavily from contemporary
functional languanges. It is designed to interoperate seamlessly with other
libraries including itertools, functools, and third party libraries. High
performance functional data analysis is possible with builtin types like list
and dict, and user-defined data structures; and low memory usage is achieved
by using the iterator protocol and returning iterators whenever possible.

cytoolz implements the same API as toolz. The main differences are that
cytoolz is faster (typically 2-5x faster with a few spectacular exceptions)
and cytoolz offers a C API that is accessible to other projects developed in
Cython. Since toolz is able to process very large (potentially infinite) data
sets, the performance increase gained by using cytoolz can be significant.

See the PyToolz documentation at http://toolz.readthedocs.org.

%prep
%setup -q -n %{srcname}-%{version}

# Remove the cythonized files in order to regenerate them during build.
rm $(grep -rl '/\* Generated by Cython')

%build
%py3_build

%install
%py3_install

%check
# Let's ignore the "breakpoint" introspection failure for now,
# breakpoint is probably only used in development.
# https://github.com/pytoolz/cytoolz/issues/122
# PYTHONPATH=%{buildroot}%{python3_sitearch} PYTHONDONTWRITEBYTECODE=1 py.test-%{python3_version} cytoolz/tests -k 'not test_introspect_builtin_modules' -v

pip3 install atomicwrites>=1.3.0 \
    attrs>=19.1.0 \
    more-itertools>=7.0.0 \
    pluggy>=0.11.0 \
    pytest>=5.4.0 \
    pytest-cov>=2.7.1 \
    toolz>=0.9.0 \
    Cython \
    CPython
python3 setup.py test
PATH=%{buildroot}%{_bindir}:${PATH} \
PYTHONPATH=%{buildroot}%{python3_sitelib} \
    python%{python3_version} -m pytest -v cytoolz/tests/*


%files -n python%{python3_pkgversion}-%{srcname}
%license LICENSE.txt
%{python3_sitearch}/%{srcname}/
%{python3_sitearch}/%{srcname}*.egg-info/
%exclude %{python3_sitearch}/.pytest_cache/

%changelog
* Wed Dec 27 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 0.12.2-1
- Auto-upgrade to 0.12.2 - none

* Wed Jun 23 2021 Rachel Menge <rachelmenge@microsoft.com> - 0.11.0-3
- Initial CBL-Mariner import from Fedora 34 (license: MIT)
- Remove python2
- License verified

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Sep 23 2020 Orion Poplawski <orion@nwra.com> - 0.11.0-1
- Update to 0.11.0

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 0.10.1-3
- Rebuilt for Python 3.9

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Nov  3 2019 Orion Poplawski <orion@nwra.com> - 0.10.1-1
- Update to 0.10.1

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 0.10.0-3
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 0.10.0-2
- Rebuilt for Python 3.8

* Tue Jul 30 2019 Orion Poplawski <orion@nwra.com> - 0.10.0-1
- Update to 0.10.0

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat Jun 01 2019 Charalampos Stratakis <cstratak@redhat.com> - 0.9.0.1-6
- Recythonize the sources

* Fri Apr 26 2019 Orion Poplawski <orion@nwra.com> - 0.9.0.1-5
- Do not ship PYTEST.pyc files (bug #1702848)
- Do not ship tests
- Run tests in build directory

* Fri Mar 08 2019 Carl George <carl@george.computer> - 0.9.0.1-4
- EPEL compatibility

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Oct 27 2018 Orion Poplawski <orion@nwra.com> - 0.9.0.1-2
- Drop Python 2 for Fedora 30+ (bug #1634987)

* Tue Jun 19 2018 Orion Poplawski <orion@nwra.com> - 0.9.0.1-1
- Update to 0.9.0.1

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 0.8.0-8
- Rebuilt for Python 3.7

* Mon Feb 12 2018 Iryna Shcherbina <ishcherb@redhat.com> - 0.8.0-7
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 0.8.0-2
- Rebuild for Python 3.6

* Thu Oct 20 2016 Orion Poplawski <orion@cora.nwra.com> - 0.8.0-1
- Update to 0.8.0

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.5-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Apr 5 2016 Orion Poplawski <orion@cora.nwra.com> - 0.7.5-1
- Initial package
