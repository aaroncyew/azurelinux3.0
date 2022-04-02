Vendor:         Microsoft Corporation
Distribution:   Mariner
Name:           afflib
Version:        3.7.19
Release:        6%{?dist}
Summary:        Library to support the Advanced Forensic Format

License:        BSD with advertising and Public Domain
URL:            https://github.com/sshock/AFFLIBv3
Source0:        %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  libtool

BuildRequires:  curl-devel
BuildRequires:  expat-devel
# GPLv2 FOSS incompatible with BSD with advertising
##BuildRequires:  fuse-devel
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
# GPLv2 FOSS incompatible with BSD with advertising
##BuildRequires:  readline-devel
#BuildRequires:  libedit-devel - good replacement for readline - not supported for now
BuildRequires:  zlib-devel
BuildRequires: make
BuildRequires:  python3
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-Cython



# Afflib format uses lzma-SDK 443
Provides: bundled(lzma) = 443



%description
AFF® is an open and extensible file format designed to store disk images and
associated metadata.
afflib is library for support of the Advanced Forensic Format (AFF).


%package -n     afftools
Summary:        Utilities for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n afftools
The %{name}-utils package contains utilities for using %{name}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       openssl-devel
Requires:       pkgconfig

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package -n python%{python3_pkgversion}-pyaff
Summary:        Python3 binding for the AFFLIB
Group:          Development/Libraries
%{?python_provide:%python_provide python%{python3_pkgversion}-pyaff}



%description -n python%{python3_pkgversion}-pyaff
Python3 bindings for AFFLIB.
These bindings currently support a read-only file-like interface to AFFLIB and
basic metadata accessor functions. The binding is not currently complete.





%prep
%autosetup -p1 -n AFFLIBv3-%{version}
# prevent internal lzma to be built - testing
#rm -rf lzma443

#fix spurious permissions with lzma443
find lzma443 -type f -exec chmod 0644 {} ';'
chmod 0644 lib/base64.{h,cpp}

./bootstrap.sh

%build
%configure --enable-shared \
  --disable-static \
  --enable-python=no \
  --enable-s3=yes

# Remove rpath from libtool
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

# clean unused-direct-shlib-dependencies
sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool

# Remove the cythonized files in order to regenerate them during build.
rm $(grep -rl '/\* Generated by Cython')

%make_build
cd pyaff
%global py_setup_args build_ext --include-dirs %{_builddir}/AFFLIBv3-%{version}/include --library-dirs %{_builddir}/AFFLIBv3-%{version}/lib/.libs
%py3_build


%install
%make_install
find %{buildroot} -name '*.la' -exec rm -f {} ';'

cd pyaff
%py3_install


%ldconfig_scriptlets


%files
%doc AUTHORS BUGLIST.txt ChangeLog NEWS README
%doc doc/announce_2.2.txt
%license COPYING
%{_libdir}/*.so.*

%files -n afftools
%{_bindir}/aff*
%{_mandir}/man1/aff*.1.*

%files devel
%doc doc/crypto_design.txt doc/crypto_doc.txt
%{_includedir}/afflib/
%{_libdir}/*.so
%{_libdir}/pkgconfig/afflib.pc

%files -n python%{python3_pkgversion}-pyaff
%license COPYING
%doc pyaff/README
%{python3_sitearch}/PyAFF*
%{python3_sitearch}/pyaff*

%changelog
* Fri Apr 01 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 3.7.19-6
- Cleaning-up spec. License verified.

* Mon Aug 09 2021 Thomas Crain <thcrain@microsoft.com> - 3.7.19-5
- Initial CBL-Mariner import from Fedora 35 (license: MIT).
- Remove Python 2 support

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.19-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri Jun 04 2021 Python Maint <python-maint@redhat.com> - 3.7.19-3
- Rebuilt for Python 3.10

* Mon Jan 25 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sun Nov 29 2020 Michal Ambroz <rebus _AT seznam.cz> - 3.7.19-1
- bump to version 3.7.19

* Fri Jul 31 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.18-11
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.18-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 3.7.18-9
- Rebuilt for Python 3.9

* Thu Feb 06 2020 Nicolas Chauvet <kwizart@gmail.com> - 3.7.18-8
- Drop libtermcap-devel merged with ncurses-devel

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.18-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 3.7.18-6
- Rebuilt for Python 3.8

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.18-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat Jun 01 2019 Charalampos Stratakis <cstratak@redhat.com> - 3.7.18-4
- Recythonize the sources

* Thu Apr 11 2019 Miro Hrončok <mhroncok@redhat.com> - 3.7.18-3
- remove python2-pyaff from Fedora

* Mon Apr 01 2019 Michal Ambroz <rebus _AT seznam.cz> - 3.7.18-2
- separate python2-pyaff / python3-pyaff packages
- fix python dependencies for EPEL build

* Mon Mar 11 2019 Michal Ambroz <rebus _AT seznam.cz> - 3.7.18-1
- bump to 3.7.18 which contains:
- Remove upstream patch Sanity-check-size-passed-to-malloc.patch
- Fix affverify failing due to context being freed too soon
- Fix pyaff build issue with newer Python (3.7) and cython (0.29)
- from version 3.7.17
- fix #34: option typo (25 minutes ago)
- minor fixes to configure.ac (3 months ago)
- Fix issue #32, an off-by-one buffer overflow (6 months ago)
- whitespace (6 months ago)
- Sanity check size passed to malloc... (6 months ago)
- Fix incrementing in vnode_split_raw.cpp for comment consistnecy (12 months ago)
- Update Win32 readmes to fix issue #26. (1 year, 2 months ago)
- build python3 package

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.16-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 07 2019 Nicolas Chauvet <kwizart@gmail.com> - 3.7.16-8
- Drop unused lzma-devel

* Tue Jul 17 2018 Miro Hrončok <mhroncok@redhat.com> - 3.7.16-7
- Update Python macros to new packaging standards
  (See https://fedoraproject.org/wiki/Changes/Move_usr_bin_python_into_separate_package)

* Tue Jul 17 2018 Nicolas Chauvet <kwizart@gmail.com> - 3.7.16-6
- Add missng cc

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.16-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Mar 12 2018 Nicolas Chauvet <kwizart@gmail.com> - 3.7.16-4
- Security issue - rhbz#1554423
- Spec file update

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.16-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Feb 06 2018 Iryna Shcherbina <ishcherb@redhat.com> - 3.7.16-2
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Mon Jan 08 2018 Nicolas Chauvet <kwizart@gmail.com> - 3.7.16-1
- Update to 3.7.16

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.15-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.15-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7.15-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Fri Mar 03 2017 Nicolas Chauvet <kwizart@gmail.com> - 3.7.15-1
- Update to 3.7.15

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7.4-5
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 3.7.4-2
- Rebuilt for GCC 5 C++11 ABI change

* Sun Jan 04 2015 Nicolas Chauvet <kwizart@gmail.com> - 3.7.4-1
- Update to 3.7.4
- cleanup spec file

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Feb 12 2014 Nicolas Chauvet <kwizart@gmail.com> - 3.7.3-1
- Update to 3.7.3

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Sep 08 2012 Nicolas Chauvet <kwizart@gmail.com> - 3.7.1-1
- Update to 3.7.1

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.15-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.15-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Jan 12 2012 Nicolas Chauvet <kwizart@gmail.com> - 3.6.15-1
- Update to 3.6.15

* Thu Sep 08 2011 Nicolas Chauvet <kwizart@gmail.com> - 3.6.12-2
- Enable S3

* Fri May 27 2011 Nicolas Chauvet <kwizart@gmail.com> - 3.6.12-1
- Update to 3.6.12

* Sat Mar 26 2011 Nicolas Chauvet <kwizart@gmail.com> - 3.6.8-1
- Update to 3.6.8

* Sun Feb 13 2011 Nicolas Chauvet <kwizart@gmail.com> - 3.6.6-1
- Update to 3.6.6

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.6.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Dec 16 2010 Nicolas Chauvet <kwizart@gmail.com> - 3.6.4-1
- Update to 3.6.4
- Disable libewf support - http://afflib.org/archives/75

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 3.5.12-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Wed Jul 14 2010 Nicolas Chauvet <kwizart@gmail.com> - 3.5.12-1
- Update to 3.4.12

* Sun Apr 18 2010 Nicolas Chauvet <kwizart@fedoraproject.org> - 3.5.10-1
- Update to 3.5.10
- Remove upstreamed patch

* Tue Jan 19 2010 Nicolas Chauvet <kwizart@fedoraproject.org> - 3.5.7-1
- Update to 3.5.7

* Fri Nov 27 2009 Nicolas Chauvet <kwizart@fedoraproject.org> - 3.5.3-1
- Update to 3.5.3

* Tue Oct 27 2009 kwizart < kwizart at gmail.com > - 3.5.2-1
- Update to 3.5.2
- Remove upstreamed patch

* Thu Sep 24 2009 kwizart < kwizart at gmail.com > - 3.4.1-1
- Update to 3.4.1
- Update gcc43 (new case)
- Enable python binding.
- Avoid version-info on the python module.

* Wed Sep  2 2009 kwizart < kwizart at gmail.com > - 3.3.7-2
- Update to 3.3.7
- Update gcc44 patch

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 3.3.6-4
- rebuilt with new openssl

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu May 21 2009 kwizart < kwizart at gmail.com > - 3.3.6-2
- Update to 3.3.6
- Add BR python-devel
- Re-introduce gcc44 patch

* Tue May 12 2009 kwizart < kwizart at gmail.com > - 3.3.5-1
- Update to 3.3.5
- Remove afflib-3.3.4-WCtype.patch

* Mon Mar  2 2009 kwizart < kwizart at gmail.com > - 3.3.4-7
- Fix for gcc44

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 15 2009 Tomas Mraz <tmraz@redhat.com> - 3.3.4-5
- rebuild with new openssl
- call libtoolize to refresh libtool

* Fri Oct  3 2008 kwizart < kwizart at gmail.com > - 3.3.4-4
- Fix release mismatch

* Fri Oct  3 2008 kwizart < kwizart at gmail.com > - 3.3.4-3
- Update to 3.3.4

* Mon Sep 15 2008 kwizart < kwizart at gmail.com > - 3.3.3-3
- Update to 3.3.3

* Thu Sep  4 2008 kwizart < kwizart at gmail.com > - 3.3.2-2
- Update gcc43 patch

* Thu Sep  4 2008 kwizart < kwizart at gmail.com > - 3.3.2-1
- Update to 3.3.2
- Remove Requires for ewftools from afftools
- Qemu image support is disabled

* Mon Sep  1 2008 kwizart < kwizart at gmail.com > - 3.3.1-1
- Update to 3.3.1

* Tue Jul 29 2008 kwizart < kwizart at gmail.com > - 3.2.5-3
- Patch with fuzz 2

* Thu Jul 24 2008 kwizart < kwizart at gmail.com > - 3.2.5-2
- Remove nos3 patch

* Thu Jul 24 2008 kwizart < kwizart at gmail.com > - 3.2.5-1
- Update to 3.2.5

* Fri Jul  4 2008 kwizart < kwizart at gmail.com > - 3.2.3-1
- Update to 3.2.3

* Thu Jun 26 2008 kwizart < kwizart at gmail.com > - 3.2.1-4
- Explicitely disable s3

* Thu Jun 26 2008 kwizart < kwizart at gmail.com > - 3.2.1-3
- Disable s3

* Wed Jun 25 2008 kwizart < kwizart at gmail.com > - 3.2.1-2
- Fix redefinition of typedef AFFILE

* Sat Jun  7 2008 kwizart < kwizart at gmail.com > - 3.2.1-1
- Update to 3.2.1

* Wed May 21 2008 kwizart < kwizart at gmail.com > - 3.2.0-1
- Update to 3.2.0

* Tue Apr 15 2008 kwizart < kwizart at gmail.com > - 3.1.6-1
- Update to 3.1.6

* Fri Mar 21 2008 kwizart < kwizart at gmail.com > - 3.1.3-4
- Fix typo

* Wed Mar 19 2008 kwizart < kwizart at gmail.com > - 3.1.3-3
- Add missing requires with pkgconfig

* Mon Mar 17 2008 kwizart < kwizart at gmail.com > - 3.1.3-2
- Rebuild with newer libewf and enable-libewf=yes
- Add pkg-config support in afflib-devel.
- Add a patch to remove ldconfig call when building the package.
- Add libtermcap-devel

* Wed Mar 12 2008 kwizart < kwizart at gmail.com > - 3.1.3-1
- Update to 3.1.3
- Disable libewf support in afflib for now.
- Disable rpath
- Fix for gcc43 and s3

* Fri Nov 30 2007 kwizart < kwizart at gmail.com > - 3.0.4-1
- Update to 3.0.4

* Sun Nov 18 2007 kwizart < kwizart at gmail.com > - 3.0.1-1
- Update to 3.0.1

* Fri Nov  2 2007 kwizart < kwizart at gmail.com > - 2.4.0-1
- Initial package for Fedora

