Summary:        Vulkan ICD desktop loader
Name:           vulkan-loader
Version:        1.2.148.1
Release:        3%{?dist}
License:        ASL 2.0
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://github.com/KhronosGroup/Vulkan-Loader
#WARNING: the source file downloads as 'sdk-%%{version}.tar.gz' and MUST be re-named to match the 'Source0' tag.
#Source0:       %%{url}/archive/sdk-%%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  ninja-build
BuildRequires:  pkg-config
BuildRequires:  python3-devel
BuildRequires:  vulkan-headers = 1.2.148.0
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xrandr)

Provides:       vulkan%{?_isa} = %{version}-%{release}
Provides:       vulkan = %{version}-%{release}
Obsoletes:      vulkan < %{version}-%{release}
Provides:       vulkan-filesystem = %{version}-%{release}
Obsoletes:      vulkan-filesystem < %{version}-%{release}

%description
This project provides the Khronos official Vulkan ICD desktop
loader for Windows, Linux, and MacOS.

%package        devel
Summary:        Development files for %{name}

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       vulkan-headers

Provides:       pkgconfig(vulkan) = %{version}-%{release}
Provides:       vulkan-devel%{?_isa} = %{version}-%{release}
Provides:       vulkan-devel = %{version}-%{release}
Obsoletes:      vulkan-devel < %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -n Vulkan-Loader-sdk-%{version}


%build
%cmake -GNinja -DCMAKE_BUILD_TYPE=Release .
%ninja_build


%install
%ninja_install

# create the filesystem
mkdir -p %{buildroot}%{_sysconfdir}/vulkan/{explicit,implicit}_layer.d/ \
%{buildroot}%{_datadir}/vulkan/{explicit,implicit}_layer.d/ \
%{buildroot}{%{_sysconfdir},%{_datadir}}/vulkan/icd.d


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSE.txt
%doc README.md CONTRIBUTING.md
%dir %{_sysconfdir}/vulkan/
%dir %{_sysconfdir}/vulkan/explicit_layer.d/
%dir %{_sysconfdir}/vulkan/icd.d/
%dir %{_sysconfdir}/vulkan/implicit_layer.d/
%dir %{_datadir}/vulkan/
%dir %{_datadir}/vulkan/explicit_layer.d/
%dir %{_datadir}/vulkan/icd.d/
%dir %{_datadir}/vulkan/implicit_layer.d/
%{_libdir}/*.so.*

%files devel
%{_libdir}/pkgconfig/vulkan.pc
%{_libdir}/*.so

%changelog
* Mon Mar 29 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.2.148.1-3
- Changed source tarball name.

* Fri Jan 15 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.2.148.1-2
- Initial CBL-Mariner import from Fedora 33 (license: MIT).
- License verified.
- Added explicit "Provides" for "pkgconfig(*)".
- Replaced 'cmake_(build|install)' macros with 'ninja_(build|install)'.
- Replaced BR 'cmake3' with 'cmake'.
- Replaced ldconfig scriptlets with explicit calls to ldconfig.

* Thu Oct 08 2020 Dave Airlie <airlied@redhat.com> - 1.2.148.1-1
- Update to 1.2.148.1 loader - fixes layer loading issue

* Tue Aug 04 2020 Dave Airlie <airlied@redhat.com> - 1.2.148.0-1
- Update to 1.2.148.0 loader

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.135.0-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.135.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Apr 22 2020 Dave Airlie <airlied@redhat.com> - 1.2.135.0-1
- Update to 1.2.135.0

* Wed Jan 29 2020 Dave Airlie <airlied@redhat.com> - 1.2.131.1-1
- Update to 1.2.131.1

* Tue Nov 12 2019 Dave Airlie <airlied@redhat.com> - 1.1.126.0-1
- Update to 1.1.126.0

* Wed Jul 31 2019 Dave Airlie <airlied@redhat.com> - 1.1.114.0-1
- Update to 1.1.114.0

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.108.0-1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Jun 25 2019 Dave Airlie <airlied@redhat.com> - 1.1.108.0-0
- Update to 1.1.108.0

* Wed Mar 06 2019 Dave Airlie <airlied@redhat.com> - 1.1.101.0-0
- Update to 1.1.101.0

* Wed Feb 13 2019 Dave Airlie <airlied@redhat.com> - 1.1.97.0-0
- Update to 1.1.97.0

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.92.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 03 2018 Dave Airlie <airlied@redhat.com> - 1.1.92.0-1
- Update to 1.1.92.0

* Mon Nov 19 2018 Dave Airlie <airlied@redhat.com> - 1.1.85.0-1
- Update to 1.1.85.0

* Tue Aug 07 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.82.0-1
- Update to 1.1.82.0

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.77.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jun 27 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-4
- Fix update path

* Tue Jun 26 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-3
- Add conditional for mesa-vulkan-drivers requires

* Tue Jun 26 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-2
- Improve description and summary
- Set release

* Sat Jun 23 2018 Leigh Scott <leigh123linux@googlemail.com> - 1.1.77.0-1
- Initial package
