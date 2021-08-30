%global tarball xf86-input-libinput
%global moduledir %(pkg-config xorg-server --variable=moduledir )
%global driverdir %{moduledir}/input

Summary:        Xorg X11 libinput input driver
Name:           xorg-x11-drv-libinput
Version:        0.30.0
Release:        4%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
URL:            https://www.x.org
Source0:        ftp://ftp.x.org/pub/individual/driver/%{tarball}-%{version}.tar.bz2
Source1:        71-libinput-overrides-wacom.conf

# Fedora-only hack for hidpi screens
# https://bugzilla.redhat.com/show_bug.cgi?id=1413306
Patch01:        0001-Add-a-DPIScaleFactor-option-as-temporary-solution-to.patch

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libevdev-devel
BuildRequires:  libinput-devel >= 0.6.0-3
BuildRequires:  libtool
BuildRequires:  systemd-devel
BuildRequires:  xorg-x11-server-devel >= 1.14.0
BuildRequires:  xorg-x11-util-macros

Requires:       Xorg
Requires:       libinput >= 0.21.0
Requires:       xkeyboard-config

Provides:       xorg-x11-drv-synaptics = 1.9.0-3
Obsoletes:      xorg-x11-drv-synaptics < 1.9.0-3

%description
A generic input driver for the X.Org X11 X server based on libinput,
supporting all devices.

%package devel
Summary:        Xorg X11 libinput input driver development package.

Requires:       pkg-config

Provides:       pkgconfig(xorg-libinput) = %{version}-%{release}

%description devel
Xorg X11 libinput input driver development files.

%prep
%autosetup -p1 -n %{tarball}-%{version}

%build
autoreconf --force -v --install || exit 1
%configure --disable-static --disable-silent-rules
make %{?_smp_mflags}

%install
%make_install

# We intentionally don't ship *.la files
find %{buildroot} -type f -name "*.la" -delete -print

cp %{SOURCE1} %{buildroot}%{_datadir}/X11/xorg.conf.d/

%files
%license COPYING
%{driverdir}/libinput_drv.so
%{_datadir}/X11/xorg.conf.d/40-libinput.conf
%{_datadir}/X11/xorg.conf.d/71-libinput-overrides-wacom.conf
%{_mandir}/man4/libinput.4*

%files devel
%license COPYING
%{_libdir}/pkgconfig/xorg-libinput.pc
%dir %{_includedir}/xorg/
%{_includedir}/xorg/libinput-properties.h

%changelog
* Fri Jan 15 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 0.30.0-4
- Initial CBL-Mariner import from Fedora 33 (license: MIT).
- License verified.
- Added explicit "Provides" for "pkgconfig(*)".
- Change BR 'libudev-devel' to 'systemd-devel', which is CBL-Mariner's equivalent.

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.30.0-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.30.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue May 19 2020 Peter Hutterer <peter.hutterer@redhat.com> 0.30.0-1
- xf86-input-libinput 0.30.0

* Fri Jan 31 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.29.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Aug 12 2019 Peter Hutterer <peter.hutterer@redhat.com> 0.29.0-1
- xf86-input-libinput 0.29.0

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.28.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Feb 04 2019 Peter Hutterer <peter.hutterer@redhat.com> 0.28.2-1
- xf86-input-libinput 0.28.2

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.28.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Oct 15 2018 Peter Hutterer <peter.hutterer@redhat.com> 0.28.1-1
- xf86-input-libinput 0.28.1

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.28.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jul 11 2018 Peter Hutterer <peter.hutterer@redhat.com> 0.28.0-1
- xf86-input-libinput 0.28.0

* Thu Apr 12 2018 Peter Hutterer <peter.hutterer@redhat.com> 0.27.1-2
- Build on s390x (#1565062)

* Tue Apr 10 2018 Peter Hutterer <peter.hutterer@redhat.com> 0.27.1-1
- xorg-x11-drv-libinput 0.27.1

* Mon Apr 02 2018 Adam Jackson <ajax@redhat.com> - 0.27.0-3
- Rebuild for xserver 1.20

* Thu Mar 22 2018 Peter Hutterer <peter.hutterer@redhat.com> 0.27.0-2
- Fix left-handed property missing on all but the first pointer device

* Tue Mar 20 2018 Peter Hutterer <peter.hutterer@redhat.com> 0.27.0-1
- xorg-x11-drv-libinput 0.27.0

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.26.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Sep 15 2017 Peter Hutterer <peter.hutterer@redhat.com> 0.26.0-1
- xorg-x11-drv-libinput 0.26.0

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.25.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.25.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu May 18 2017 Peter Hutterer <peter.hutterer@redhat.com> 0.25.1-2
- Add a new option to provide a workaround for the slow pointer movement on
  hidpi displays (#1413306) .
  That's a fedora-only patch for now, no idea what the permanent upstream
  solution will be here.

* Fri May 05 2017 Peter Hutterer <peter.hutterer@redhat.com> 0.25.1-1
- xorg-x11-drv-libinput 0.25.1

* Thu Mar 09 2017 Peter Hutterer <peter.hutterer@redhat.com> 0.25.0-1
- libinput 0.25.0

* Thu Feb 09 2017 Peter Hutterer <peter.hutterer@redhat.com> 0.24.0-1
- libinput 0.24.0

* Wed Dec 21 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.23.0-2
- Ignore LED updates for disabled devices, avoids a null-pointer dereference
  when an AccessX timeout is set

* Mon Dec 12 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.23.0-1
- libnput 0.23.0

* Fri Nov 25 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.22.0-4
- Override touchpads assigned the wacom driver with libinput again
  (#1397477)

* Fri Nov 18 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.22.0-3
- Provide xorg-x11-drv-synaptics. The actual content is now provided by
  xorg-x11-drv-synaptics-legacy (#1394836). For details, see
  https://fedoraproject.org/wiki/Changes/RetireSynapticsDriver

* Tue Nov 01 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.22.0-2
- Match against tablets too

* Wed Oct 19 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.22.0-1
- xf86-input-libinput 0.22.0

* Tue Oct 18 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.20.0-1
- xf86-input-libinput 0.20.0

* Thu Sep 29 2016 Hans de Goede <hdegoede@redhat.com> 0.19.1-3.20160929
- Fix crash when the first detected input device gets removed (rhbz#1381840)

* Thu Sep 29 2016 Hans de Goede <hdegoede@redhat.com> 0.19.1-2.20160929
- Update to latest git master for use with xserver-1.19
- Rebuild against xserver-1.19

* Wed Sep 14 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.19.1-1
- xf86-input-libinput 0.19.1

* Tue Jul 19 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.19.0-2
- Bump to make F24 update path happy

* Thu Apr 28 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.19.0-1
- xf86-input-libinput 0.19.0

* Fri Feb 26 2016 Peter Hutterer <peter.hutterer@redhat.com> 0.17.0-1
- xf86-input-libinput 0.17.0

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.16.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Dec 23 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.16.0-1
- xf86-input-libinput 0.16.0

* Tue Oct 27 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.15.0-1
- xf86-input-libinput 0.15.0

* Wed Sep 16 2015 Dave Airlie <airlied@redhat.com> - 0.14.0-2
- 1.18 ABI rebuild

* Mon Aug 31 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.14.0-1
- xf86-input-libinput 0.14.0

* Mon Aug 17 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.13.0-2
- Add drag lock support (#1249309)

* Tue Aug 11 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.13.0-1
- xf86-input-libinput 0.13.0

* Wed Jul 29 2015 Dave Airlie <airlied@redhat.com> 0.12.0-2
- bump for X server ABI

* Tue Jul 14 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.12.0-1
- xf86-input-libinput 0.12.0

* Mon Jul 13 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.11.0-3
- Restore unaccelerated valuator masks (#1208992)

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 15 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.11.0-1
- xf86-input-libinput 0.11.0
- support buttons higher than BTN_BACK (1230945)

* Mon Jun 01 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.10.0-5
- Fix missing scroll button property

* Fri May 29 2015 Nils Philippsen <nils@redhat.com> 0.10.0-4
- fix URL

* Tue May 26 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.10.0-3
- Use the new unnaccelerated valuator masks, fixes nonmoving mouse in SDL
  (#1208992)

* Fri May 22 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.10.0-2
- Init mixed rel/abs devices as rel devices (#1223619)

* Thu May 21 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.10.0-1
- xf86-input-libinput 0.10.0

* Thu Apr 23 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.9.0-1
- xf86-input-libinput 0.9.0

* Tue Mar 10 2015 Peter Hutterer <peter.hutterer@redhat.com> - 0.8.0-2
- Rebuild for libinput soname bump

* Fri Mar 06 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.8.0-1
- xf86-input-libinput 0.8.0

* Thu Mar 05 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.7.0-5
- Fix two-finger scrolling speed (#1198467)

* Thu Feb 26 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.7.0-4
- Fix property setting patch, first version prevented re-enabling a device.

* Wed Feb 25 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.7.0-3
- Fix a crash when setting properties on a disabled device

* Wed Feb 25 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.7.0-2
- Fix stack smash on pointer init (#1195905)

* Tue Feb 24 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.7.0-1
- xorg-x11-drv-libinput 0.7.0

* Tue Jan 27 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.6.0-1
- xorg-x11-drv-libinput 0.6.0

* Fri Jan 16 2015 Peter Hutterer <peter.hutterer@redhat.com> 0.5.0-1
- xorg-x11-drv-libinput 0.5.0

* Fri Dec 05 2014 Peter Hutterer <peter.hutterer@redhat.com> 0.4.0-1
- xorg-x11-drv-libinput 0.4.0

* Mon Nov 24 2014 Peter Hutterer <peter.hutterer@redhat.com> 0.3.0-1
- xorg-x11-drv-libinput 0.3.0

* Mon Nov 24 2014 Peter Hutterer <peter.hutterer@redhat.com> 0.2.0-2
- Add explicit (Build)Requires for libinput 0.6.0-3, we rely on new symbols
  from the git snapshot

* Mon Nov 24 2014 Peter Hutterer <peter.hutterer@redhat.com> 0.2.0-1
- Only match on specific device types, don't match on joysticks or tablets
- libinput 0.2.0
- switch to new fdo host

* Fri Sep 12 2014 Peter Hutterer <peter.hutterer@redhat.com> - 0.1.2-3
- Rebuild for libinput soname bump

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 24 2014 Peter Hutterer <peter.hutterer@redhat.com> 0.1.2-1
- Update to 0.1.2, dropping the pkgconfig files

* Thu Jun 26 2014 Peter Hutterer <peter.hutterer@redhat.com> 0.1.1-1
- Initial release (#1113392)
