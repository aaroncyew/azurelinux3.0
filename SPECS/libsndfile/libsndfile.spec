Summary:        Library for reading and writing sound files
Name:           libsndfile
Version:        1.0.31
Release:        1%{?dist}
License:        BSD AND GPLv2+ AND LGPLv2+ AND MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            http://www.mega-nerd.com/libsndfile/
#Source0:        https://github.com/libsndfile/libsndfile/archive/%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz

Patch0:         libsndfile-1.0.31-system-gsm.patch
Patch1:         libsndfile-1.0.25-zerodivfix.patch
Patch2:         revert.patch

# CVE disputed by project's owner, no repro.
# See here for more details: https://github.com/libsndfile/libsndfile/issues/398.
Patch100:       CVE-2018-13419.nopatch

BuildRequires:  alsa-lib-devel
BuildRequires:  autogen
BuildRequires:  gcc
BuildRequires:  gsm-devel
BuildRequires:  libtool
BuildRequires:  pkg-config
BuildRequires:  sqlite-devel

%description
libsndfile is a C library for reading and writing sound files such as
AIFF, AU, WAV, and others through one standard interface. It can
currently read/write 8, 16, 24 and 32-bit PCM files as well as 32 and
64-bit floating point WAV files and a number of compressed formats. It
compiles and runs on *nix, MacOS, and Win32.

%package devel
Summary:        Development files for libsndfile

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkg-config

Provides:       pkgconfig(sndfile) = %{version}-%{release}

%description devel
libsndfile is a C library for reading and writing sound files such as
AIFF, AU, WAV, and others through one standard interface.
This package contains files needed to develop with libsndfile.

%package utils
Summary:        Command Line Utilities for libsndfile

Requires:       %{name} = %{version}-%{release}

%description utils
libsndfile is a C library for reading and writing sound files such as
AIFF, AU, WAV, and others through one standard interface.
This package contains command line utilities for libsndfile.

%prep
%autosetup -p1
rm -r src/GSM610

%build
autoreconf -I M4 -fiv # for system-gsm patch
%configure \
    --disable-dependency-tracking \
    --enable-sqlite \
    --enable-alsa \
    --enable-largefile \
    --disable-static

# Get rid of rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

%make_build


%install
%make_install

# Removing docs and static libs
rm -rf %{buildroot}%{_docdir}/%{name}
find %{buildroot} -type f -name "*.la" -delete -print

# fix multilib issues
mv %{buildroot}%{_includedir}/sndfile.h \
   %{buildroot}%{_includedir}/sndfile-%{__isa_bits}.h

cat > %{buildroot}%{_includedir}/sndfile.h <<EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
# include "sndfile-32.h"
#elif __WORDSIZE == 64
# include "sndfile-64.h"
#else
# error "unexpected value for __WORDSIZE macro"
#endif
EOF

%check
LD_LIBRARY_PATH=$PWD/src/.libs make check


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license COPYING
%doc AUTHORS README NEWS
%{_libdir}/%{name}.so.*

%files utils
%{_bindir}/sndfile-cmp
%{_bindir}/sndfile-concat
%{_bindir}/sndfile-convert
%{_bindir}/sndfile-deinterleave
%{_bindir}/sndfile-info
%{_bindir}/sndfile-interleave
%{_bindir}/sndfile-metadata-get
%{_bindir}/sndfile-metadata-set
%{_bindir}/sndfile-play
%{_bindir}/sndfile-salvage
%{_mandir}/man1/sndfile-cmp.1*
%{_mandir}/man1/sndfile-concat.1*
%{_mandir}/man1/sndfile-convert.1*
%{_mandir}/man1/sndfile-deinterleave.1*
%{_mandir}/man1/sndfile-info.1*
%{_mandir}/man1/sndfile-interleave.1*
%{_mandir}/man1/sndfile-metadata-get.1*
%{_mandir}/man1/sndfile-metadata-set.1*
%{_mandir}/man1/sndfile-play.1*
%{_mandir}/man1/sndfile-salvage.1*

%files devel
%doc ChangeLog
%{_includedir}/sndfile.h
%{_includedir}/sndfile.hh
%{_includedir}/sndfile-%{__isa_bits}.h
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/sndfile.pc

%changelog
* Tue Feb 09 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0.31-1
- Added "autogen" to "BuildRequires" to build the newer version.
- Added a .nopatch for CVE-2018-13419 (existence of issue disputed by project owner).
- Updated version to 1.0.31 to fix the following CVEs:
-   2017-6892, 2017-8361, 2017-8362, 2017-8363, 2017-8365, 2017-12562, 2017-14245, 2017-14246, 2017-14634,
-   2018-13139, 2018-19432, 2018-19661, 2018-19662, 2018-19758,
-   2019-3832.
- Removing outdated patches.
* Tue Jan 19 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0.28-14
- Initial CBL-Mariner import from Fedora 33 (license: MIT).
- License verified.
- Added explicit "Provides" for "pkgconfig(*)".
- Removed documentation.
- Removed support for FLAC and Vorbis/Ogg, since they are not required for CBL-Mariner.
- Renamed CVE patches to CBL-Mariner's "CBL-YYYY-NNNNN" format.
- Replaced ldconfig scriptlets with explicit calls to ldconfig.

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.28-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.28-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.28-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.28-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.28-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Mar 07 2018 Michal Hlavinka <mhlavink@redhat.com> - 1.0.28-8
- add gcc buildrequire

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.28-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 24 2017 Michal Hlavinka <mhlavink@redhat.com> - 1.0.28-6
- heap-based Buffer Overflow in psf_binheader_writef function (#1483140, CVE-2017-12562)

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.28-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.28-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jun 21 2017 Michal Hlavinka <mhlavink@redhat.com> - 1.0.28-3
- fix buffer overflow in aiff (CVE-2017-6892,rhbz#1463328)

* Mon Jun 05 2017 Michal Hlavinka <mhlavink@redhat.com> - 1.0.28-2
- fix flac and pcm buffer overflows (CVE-2017-8361,CVE-2017-8362,CVE-2017-8363,CVE-2017-8365)

* Tue Apr 11 2017 Michal Hlavinka <mhlavink@redhat.com> - 1.0.28-1
- updated to 1.0.28
- fix possible buffer overflow when parsing crafted ID3 tags (#1440758, CVE-2017-7586)
- fix possible buffer overflow when parsing crafted flac file (#1440756, CVE-2017-7585)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.27-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Nov 11 2016 Michal Hlavinka <mhlavink@redhat.com> - 1.0.27-1
- updated to 1.0.27

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.25-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Nov 06 2015 Michal Hlavinka <mhlavink@redhat.com> - 1.0.25-19
- fix incomplete patch for CVE-2015-7805

* Fri Nov 06 2015 Michal Hlavinka <mhlavink@redhat.com> - 1.0.25-18
- fix CVE-2015-7805: Heap overflow vulnerability when parsing specially
  crafted AIFF header

* Thu Aug 27 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 1.0.25-17
- Use __isa_bits macro instead of list of 64-bit architectures

* Sun Jul 19 2015 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.25-16
- Fix FTBFS
- Use %%license

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.25-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jan 13 2015 Michal Hlavinka <mhlavink@redhat.com> - 1.0.25-14
- fix CVE-2014-9496: 2 buffer overruns in sd2_parse_rsrc_fork (#1178840)
- division by zero leading to denial of service in psf_fwrite (#1177254)

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.25-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Aug 02 2014 Kalev Lember <kalevlember@gmail.com> - 1.0.25-12
- Fix up previous commit

* Sat Aug  2 2014 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.25-11
- Modernise spec
- Generic 32/64bit platform detection

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.25-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Jan 13 2014 Michal Hlavinka <mhlavink@redhat.com> - 1.0.25-9
- fix ppc64le build (#1051639)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.25-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 03 2013 Michal Hlavinka <mhlavink@redhat.com> - 1.0.25-7
- fix support for aarch64, another part (#969831)

* Wed Mar 27 2013 Michal Hlavinka <mhlavink@redhat.com> - 1.0.25-6
- fix support for aarch64 (#925887)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.25-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.25-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.25-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Nov 12 2011 Ville Skyttä <ville.skytta@iki.fi> - 1.0.25-2
- Patch to use system libgsm instead of a bundled copy.
- Make main package dep in -devel ISA qualified.
- Drop -octave Provides (not actually built with octave > 3.0).
- Don't build throwaway static lib.
- Run test suite during build.

* Thu Jul 14 2011 Michal Hlavinka <mhlavink@redhat.com> - 1.0.25-1
- Update to 1.0.25
- fixes integer overflow by processing certain PAF audio files (#721240)

* Sun Mar 27 2011 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 1.0.24-1
- Update to 1.0.24

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.23-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Oct 16 2010 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 1.0.23-1
- Update to 10.0.23

* Tue Oct 05 2010 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 1.0.22-1
- Update to 10.0.22

* Tue May 11 2010 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 1.0.21-1
- Update to 10.0.21
- Do not include the static library in the package (RHBZ#556074)
- Remove BR on jack since sndfile-jackplay is not provided anymore

* Mon Feb  1 2010 Stepan Kasal <skasal@redhat.com> - 1.0.20-5
- Do not build against Jack on RHEL
- Fix the Source0: URL
- Fix the licence tag

* Sat Nov 14 2009 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 1.0.20-4
- Split utils into a subpackage

* Sat Nov 14 2009 Orcan Ogetbil <oget[dot]fedora[at]gmail[dot]com> - 1.0.20-3
- Add FLAC/Ogg/Vorbis support (BR: libvorbis-devel)
- Make build verbose
- Remove rpath
- Fix ChangeLog encoding
- Move the big Changelog to the devel package

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat Jun 06 2009 Lennart Poettering <lpoetter@redhat.com> - 1.0.20-1
- Updated to 1.0.20

* Tue Mar 03 2009 Robert Scheck <robert@fedoraproject.org> - 1.0.17-8
- Rebuilt against libtool 2.2

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.17-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Oct 25 2008 Andreas Thienemann <andreas@bawue.net> - 1.0.17-6
- Removed spurious #endif in the libsndfile.h wrapper. Thx to Edward
  Sheldrake for finding it. Fixes #468508.
- Fix build for autoconf-2.63

* Thu Oct 23 2008 Andreas Thienemann <andreas@bawue.net> - 1.0.17-5
- Fixed multilib conflict. #342401
- Made flac support actually work correctly.

* Thu Aug  7 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.0.17-4
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.0.17-3
- Autorebuild for GCC 4.3

* Thu Sep 20 2007 Andreas Thienemann <andreas@bawue.net> - 1.0.17-2
- Adding FLAC support to libsndfile courtesy of gentoo, #237575
- Fixing CVE-2007-4974. Thanks to the gentoo people for the patch, #296221

* Fri Sep 08 2006 Andreas Thienemann <andreas@bawue.net> - 1.0.17-1
- Updated to 1.0.17

* Sun Apr 30 2006 Andreas Thienemann <andreas@bawue.net> - 1.0.16-1
- Updated to 1.0.16

* Thu Mar 30 2006 Andreas Thienemann <andreas@bawue.net> - 1.0.15-1
- Updated to 1.0.15

* Thu Mar 16 2006 Dams <anvil[AT]livna.org> - 1.0.14-1.fc5
- Updated to 1.0.14
- Dropped patch0

* Thu May 12 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.0.11-3
- rebuilt

* Sat Mar  5 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.0.11-2
- Fix format string bug (#149863).
- Drop explicit Epoch 0.

* Sat Dec  4 2004 Ville Skyttä <ville.skytta@iki.fi> - 0:1.0.11-0.fdr.1
- Update to 1.0.11.

* Wed Oct 13 2004 Ville Skyttä <ville.skytta@iki.fi> - 0:1.0.10-0.fdr.1
- Update to 1.0.10, update URLs, include ALSA support.
- Disable dependency tracking to speed up the build.
- Add missing ldconfig invocations.
- Make -devel require pkgconfig.
- Include developer docs in -devel.
- Provide -octave in main package, own more related dirs.
- Bring specfile up to date with current spec templates.

* Sat Apr 12 2003 Dams <anvil[AT]livna.org>
- Initial build.
