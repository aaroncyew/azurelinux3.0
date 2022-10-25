
Name:           flatbuffers
Version:        2.0.8
# The .so version is explicitly constructed from project version—search
# CMakeLists.txt for FlatBuffers_Library_SONAME_MAJOR and
# FlatBuffers_Library_SONAME_FULL—but we manually repeat the SOVERSION here,
# and use the macro in the file lists, as a reminder to avoid undetected .so
# version bumps.
%global so_version 2
Release:        1%{?dist}
Summary:        Memory efficient serialization library

# The entire source code is Apache-2.0. Even code from grpc, which is
# BSD-3-Clause in its upstream, is intended to be Apache-2.0 in this project.
# (Google is the copyright holder for both projects, so it can relicense at
# will.) See https://github.com/google/flatbuffers/pull/7073.
License:        Apache-2.0
URL:            https://google.github.io/flatbuffers
Source0:        https://github.com/google/flatbuffers/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
# The ninja backend should be slightly faster than make, with no disadvantages.
BuildRequires:  ninja-build
BuildRequires:  python3-devel
BuildRequires:  python3-packaging
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip

# From grpc/README.md:
#
#   NOTE: files in `src/` are shared with the GRPC project, and maintained
#   there (any changes should be submitted to GRPC instead). These files are
#   copied from GRPC, and work with both the Protobuf and FlatBuffers code
#   generator.
#
# It’s not clearly documented which GPRC version is excerpted, but see
# https://github.com/google/flatbuffers/pull/4305 for more details.
#
# It is not possible to unbundle this because private/internal APIs are used.
Provides:       bundled(grpc)

%global common_description %{expand:
FlatBuffers is a cross platform serialization library architected for maximum
memory efficiency. It allows you to directly access serialized data without
parsing/unpacking it first, while still having great forwards/backwards
compatibility.}

%description %{common_description}

BuildArch:      noarch


%package -n     python3-flatbuffers
Summary:        FlatBuffers serialization format for Python

BuildArch:      noarch

Recommends:     python3dist(numpy)

Provides:       flatbuffers-python3 = %{version}-%{release}
Obsoletes:      flatbuffers-python3 < 2.0.0-6

%description -n python3-flatbuffers %{common_description}

This package contains the Python runtime library for use with the Flatbuffers
serialization format.


%prep
%autosetup
%py3_shebang_fix samples

# flattests fails if out-of-source build directory is used
# https://github.com/google/flatbuffers/issues/7282
#
# This downstream-only patch is not general; it makes assumptions about the
# out-of-source build path and would break in-source builds.
sed -r -i 's@//((include|monster)_test)@//../../tests/\1@g' \
    tests/test.cpp tests/reflection_test.cpp


%generate_buildrequires
pushd python >/dev/null
%pyproject_buildrequires
popd >/dev/null


%build
# Needed for correct Python wheel version
export VERSION='%{version}'
%set_build_flags

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DFLATBUFFERS_BUILD_SHAREDLIB=ON \
    -DFLATBUFFERS_BUILD_FLATLIB=OFF \
    -DFLATBUFFERS_BUILD_FLATC=ON
%cmake_build

pushd python
%pyproject_wheel
popd



%install
%cmake_install
pushd python
%pyproject_install
%pyproject_save_files flatbuffers
popd



%check
# Upstream does not appear to provide any dedicated Python tests.
%pyproject_check_import



%files -n python3-flatbuffers -f %{pyproject_files}
%license LICENSE.txt


%changelog
* Mon Oct 24 2022 Riken Maharjan <rmaharjan@microsoft.com> - 2.0.8-1
- Initial CBL-Mariner import from Fedora 37 (license: MIT).
- License verified.

* Sat Jun 18 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 2.0.0-6
- Fix cmake invocation (fix RHBZ#2045385)
- Re-enable the tests
- Move the unversioned .so file link to the devel package
- Fix unowned %%{_libdir}/cmake/flatbuffers directory
- Move flatc to a new flatbuffers-compiler subpackage
- Fix the Python library subpackage: rename it to python3-flatbuffers, make it
  noarch, build it with pyproject-rpm-macros, add an import-only “smoke test”,
  and add a weak dependency on numpy
- Stop maintaining a flatbuffers.7 man page
- Update flatc.1 man page
- Add a -doc subpackage with samples (no reference manual for now)

* Mon Jun 13 2022 Python Maint <python-maint@redhat.com> - 2.0.0-5
- Rebuilt for Python 3.11

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri Jun 04 2021 Python Maint <python-maint@redhat.com> - 2.0.0-2
- Rebuilt for Python 3.10

* Mon May 17 2021 Benjamin Lowry <ben@ben.gmbh - 2.0.0-1
- flatbuffers 2.0.0

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Aug 10 2020 Cristian Balint <cristian.balint@gmail.com> - 1.12.0-5
- Enable python module

* Sat Aug 01 2020 Benjamin lowry <ben@ben.gmbh> - 1.12.0-4
- Update to new cmake macros, fix build error

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue May 12 2020 Benjamin Lowry <ben@ben.gmbh> - 1.12.0-1
- Upgrade to 1.12.0, fix compilation on F32

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.11.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.11.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed May 15 2019 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.11.0-1
- Update to 1.11.0

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 21 2019 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.10.0-3
- Add explicit curdir on CMake invocation

* Thu Jan 10 2019 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.10.0-2
- Fix generator (and generated tests) for gcc9 (ignore -Wclass-memaccess)

* Thu Oct 04 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.10.0-1
- Update to 1.10.0

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.9.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Apr 06 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.9.0-1
- Update to 1.9.0

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.8.0-3
- Fix build errors.

* Wed Nov 22 2017 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.8.0-2
- Update manpages for 1.8.0

* Wed Nov 22 2017 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.8.0-1
- Update to 1.8.0

* Thu Nov 2 2017 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.7.1-1
- Initial version

* Mon Mar 30 2015 Daniel Vrátil <dvratil@redhat.com> - 1.0.3-1
- Initial version (abandoned at #1207208)

