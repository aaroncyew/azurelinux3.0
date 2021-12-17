Summary:	Noninteractive ssh password provider
Name:		sshpass
Version:	1.06
Release:        4%{?dist}
License:	GPLv2+
URL:		http://sourceforge.net/projects/sshpass/
Source0:	http://downloads.sourceforge.net/project/sshpass/%{name}/%{version}/%{name}-%{version}.tar.gz
Group:		Applications/Networking
Vendor:         Microsoft Corporation
Distribution:   Mariner
Requires:       openssh

%description
sshpass is a utility designed for running ssh using the mode referred to as "keyboard-interactive" password authentication, but in non-interactive mode.
%prep
%setup -q

%build
./configure --prefix=%{_prefix}
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make prefix=%{_prefix}	DESTDIR=%{buildroot} install

%files
%defattr(-,root,root)
%license COPYING
%doc AUTHORS ChangeLog NEWS
%{_bindir}
%{_mandir}/man1

%changelog
* Thu Dec 16 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.06-4
- Removing the explicit %%clean stage.
- License verified.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 1.06-3
- Added %%license line automatically

*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 1.06-2
-   Initial CBL-Mariner import from Photon (license: Apache2).
*       Wed Apr 12 2017 Vinay Kulkarni <kulkarniv@vmware.com> 1.06-1
-       Update to version 1.06
*       Mon Oct 04 2016 ChangLee <changlee@vmware.com> 1.05-4
-       Modified %check
*	Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 1.05-3
-	GA - Bump release of all rpms
*	Thu Apr 28 2016 Anish Swaminathan <anishs@vmware.com> 1.05-2
-	Add requires for openssh
*	Fri Sep 11 2015 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 1.05-1
-	Initial version
