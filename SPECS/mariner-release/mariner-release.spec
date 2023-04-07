Summary:        CBL-Mariner release files
Name:           mariner-release
Version:        2.0
Release:        36%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Base
URL:            https://aka.ms/cbl-mariner
# Allows package management tools to find and set the default value
# for the "releasever" variable from the RPM database.
Provides:       system-release(releasever)
BuildArch:      noarch

%description
Azure CBL-Mariner release files such as yum configs and other %{_sysconfdir}/ release related files

%install
install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}/%{_libdir}

echo "CBL-Mariner %{mariner_release_version}" > %{buildroot}%{_sysconfdir}/mariner-release
echo "MARINER_BUILD_NUMBER=%{mariner_build_number}" >> %{buildroot}%{_sysconfdir}/mariner-release

cat > %{buildroot}%{_sysconfdir}/lsb-release <<- "EOF"
DISTRIB_ID="Mariner"
DISTRIB_RELEASE="%{mariner_release_version}"
DISTRIB_CODENAME=Mariner
DISTRIB_DESCRIPTION="CBL-Mariner %{mariner_release_version}"
EOF

version_id=`echo %{mariner_release_version} | grep -o -E '[0-9]+.[0-9]+' | head -1`
cat > %{buildroot}/%{_libdir}/os-release << EOF
NAME="Common Base Linux Mariner"
VERSION="%{mariner_release_version}"
ID=mariner
VERSION_ID="$version_id"
PRETTY_NAME="CBL-Mariner/Linux"
ANSI_COLOR="1;34"
HOME_URL="%{url}"
BUG_REPORT_URL="%{url}"
SUPPORT_URL="%{url}"
EOF

ln -sv ../usr/lib/os-release %{buildroot}%{_sysconfdir}/os-release

cat > %{buildroot}%{_sysconfdir}/issue <<- EOF
Welcome to CBL-Mariner %{mariner_release_version} (%{_arch}) - Kernel \r (\l)
EOF

cat > %{buildroot}%{_sysconfdir}/issue.net <<- EOF
Welcome to CBL-Mariner %{mariner_release_version} (%{_arch})
EOF

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/mariner-release
%config(noreplace) %{_sysconfdir}/lsb-release
%config(noreplace) %{_libdir}/os-release
%config(noreplace) %{_sysconfdir}/os-release
%config(noreplace) %{_sysconfdir}/issue
%config(noreplace) %{_sysconfdir}/issue.net

%changelog
* Thu Apr 06 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-36
- Updating version for April update.

* Thu Mar 02 2023 Andrew Phelps <anphel@microsoft.com> - 2.0-35
- Updating version for March 2023 update 1.

* Tue Feb 14 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-34
- Updating version for February update 2.

* Tue Feb 07 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-33
- Updating version for February update.

* Tue Jan 24 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-32
- Updating version for January update 2.

* Thu Jan 05 2023 Jon Slobodzian <joslobo@microsoft.com> - 2.0-31
- Updating version for January update.

* Mon Dec 19 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-30
- Updating version for December update 3.

* Sat Dec 10 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-29
- Updating version for December update 2.

* Thu Dec 01 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-28
- Updating version for December update.

* Mon Nov 21 2022 Mandeep Plaha <mandeepplaha@microsoft.com> - 2.0.27
- Updating version for November update 2.

* Wed Nov 09 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-26
- Updating version for November update.

* Sat Oct 29 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-25
- Updating version for a full October release.

* Tue Oct 25 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-24
- Updating version for October update.

* Fri Oct 07 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-23
- Updating version for October release.

* Fri Sep 23 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-22
- Updating version for September update 3.

* Fri Sep 16 2022 Andrew Phelps <anphel@microsoft.com> - 2.0.21
- Updating version for September update 2.

* Thu Sep 08 2022 Minghe Ren <mingheren@microsoft.com> - 2.0-20
- remove issue.net kernel part as sshd doesn't support the old-style telnet escape sequences

* Thu Sep 08 2022 Andrew Phelps <anphel@microsoft.com> - 2.0-19
- Updating version for September CVE update.

* Tue Aug 16 2022 Andrew Phelps <anphel@microsoft.com> - 2.0-18
- Updating version for August update 2.

* Wed Aug 03 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-17
- Updating version for August update.

* Tue Jul 26 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-16
- Updating version for July update 2.

* Fri Jul 08 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-15
- Updating version for July update.

* Sat Jun 25 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-14
- Updating version for June update 2.

* Wed Jun 08 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-13
- Updating version for June update.

* Sat May 21 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-12
- Updating version for May update.

* Tue Apr 19 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-11
- Updating version for GA Release Candidate

* Sat Apr 16 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-10
- Updating version for Preview-H Release.

* Sat Apr 09 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-9
- Updating version for Preview-G Release.

* Wed Mar 30 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-8
- Updating version for Preview-F Release.

* Fri Mar 4 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-7
- Updating version for Preview-E Release

* Thu Feb 24 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.0-6
- Surrounding 'VERSION_ID' inside 'os-release' with double quotes.

* Sun Feb 06 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-5
- Updating version for Preview D-Release

* Wed Jan 19 2022 Jon Slobodzian <joslobo@microsoft.com> - 2.0-4
- CBL-Mariner 2.0 Public Preview C Release.
- License verified

* Thu Dec 16 2021 Jon Slobodzian <joslobo@microsoft.com> - 2.0-3
- CBL-Mariner 2.0 Public Preview B Release version with fixed repo configuration files.

* Mon Dec 13 2021 Jon Slobodzian <joslobo@microsoft.com> - 2.0-2
- CBL-Mariner 2.0 Public Preview A Release version.

* Thu Jul 29 2021 Jon Slobodzian <joslobo@microsoft.com> - 2.0-1
- Updating version and distrotag for future looking 2.0 branch.  Formatting fixes.
- Remove %%clean section, buildroot cleaning step (both automatically done by RPM)

* Wed Apr 27 2021 Jon Slobodzian <joslobo@microsoft.com> - 1.0-16
- Updating version for April update

* Tue Mar 30 2021 Jon Slobodzian <joslobo@microsoft.com> - 1.0-15
- Updating version for March update

* Mon Feb 22 2021 Jon Slobodzian <joslobo@microsoft.com> - 1.0-14
- Updating version for February update

* Sun Jan 24 2021 Jon Slobodzian <joslobo@microsoft.com> - 1.0-13
- Updating version for January update

* Mon Dec 21 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0-12
- Updating version for December update.

* Fri Nov 20 2020 Nicolas Guibourge <nicolasg@microsoft.com> - 1.0-11
- Updating version for November update

* Sat Oct 24 2020 Jon Slobodzian <joslobo@microsoft.com> - 1.0-10
- Updating version for October update

* Fri Sep 04 2020 Mateusz Malisz <mamalisz@microsoft.com> - 1.0-9
- Remove empty %%post section, dropping dependency on /bin/sh

* Tue Aug 24 2020 Jon Slobodzian <joslobo@microsoft.com> - 1.0-8
- Changing CBL-Mariner ID from "Mariner" to "mariner" to conform to standard.  Also updated Distrib-Description and Name per internal review.

* Tue Aug 18 2020 Jon Slobodzian <joslobo@microsoft.com> - 1.0-7
- Restoring correct Name, Distribution Name, CodeName and ID.

* Fri Jul 31 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0-6
- Updating distribution name.

* Wed Jul 29 2020 Nick Samson <nisamson@microsoft.com> - 1.0-5
- Updated os-release file and URL to reflect project naming

* Wed Jun 24 2020 Jon Slobodzian <joslobo@microsoft.com> - 1.0-4
- Updated license for 1.0 release.

* Mon May 04 2020 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0-3
- Providing "system-release(releasever)" for the sake of DNF
- and other package management tools.

* Thu Jan 30 2020 Jon Slobodzian <joslobo@microsoft.com> 1.0-2
- Remove Microsoft name from distro version.

* Wed Sep 04 2019 Mateusz Malisz <mamalisz@microsoft.com> 1.0-1
- Original version for CBL-Mariner.
