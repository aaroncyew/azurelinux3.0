Vendor:         Microsoft Corporation
Distribution:   Mariner
#
# spec file for package apache-commons-cli
#
# Copyright (c) 2019 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%global base_name       cli
%global short_name      commons-%{base_name}
Name:           apache-commons-cli
Version:        1.4
Release:        4%{?dist}
Summary:        Command Line Interface Library for Java
License:        Apache-2.0
Group:          Development/Libraries/Java
URL:            http://commons.apache.org/%{base_name}/
Source0:        http://www.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
Source1:        %{name}-build.xml.tar.bz2
Patch0:         CLI-253-workaround.patch
BuildRequires:  ant
BuildRequires:  fdupes
BuildRequires:  java-devel >= 1.8
BuildRequires:  javapackages-local-bootstrap
Requires:       java >= 1.8
Provides:       jakarta-%{short_name} = %{version}-%{release}
Obsoletes:      jakarta-%{short_name} < %{version}
Provides:       apache-cli = %{version}
Obsoletes:      apache-cli < %{version}
BuildArch:      noarch

%description
The CLI library provides an API for working with the
command line arguments and options.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Documentation/HTML
Provides:       jakarta-%{short_name}-javadoc = %{version}
Obsoletes:      jakarta-%{short_name}-javadoc < %{version}

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q -n %{short_name}-%{version}-src -a1
%patch0 -p1

%pom_remove_parent

%build
ant -Dmaven.mode.offline=true package javadoc \
    -Dmaven.test.skip=true \
    -lib %{_datadir}/java

%install
# jars
install -Dpm 644 target/%{short_name}-%{version}.jar %{buildroot}%{_javadir}/%{short_name}.jar
ln -sf %{short_name}.jar %{buildroot}%{_javadir}/%{name}.jar

# pom
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml %{buildroot}%{_mavenpomdir}/%{short_name}.pom
%add_maven_depmap %{short_name}.pom %{short_name}.jar -a "org.apache.commons:%{short_name}"

# javadoc
install -d -m 0755 %{buildroot}%{_javadocdir}/%{name}
cp -pr target/site/api*/* %{buildroot}%{_javadocdir}/%{name}
%fdupes -s %{buildroot}%{_javadocdir}/%{name}

%files -f .mfiles
%license LICENSE.txt NOTICE.txt
%doc README.md RELEASE-NOTES.txt
%{_javadir}/%{name}.jar

%files javadoc
%license LICENSE.txt
%{_javadocdir}/%{name}

%changelog
* Thu Oct 14 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.4-4
- Converting the 'Release' tag to the '[number].[distribution]' format.

* Thu Nov 12 2020 Joe Schmitt <joschmit@microsoft.com> - 1.4-3.7
- Initial CBL-Mariner import from openSUSE Tumbleweed (license: same as "License" tag).
- Use javapackages-local-bootstrap to avoid build cycle.
* Mon Mar 25 2019 Fridrich Strba <fstrba@suse.com>
- Remove pom parent, since we don't use it when not building with
  maven
* Tue Feb  5 2019 Jan Engelhardt <jengelh@inai.de>
- Trim bias from description; update RPM groups.
* Tue Feb  5 2019 Fridrich Strba <fstrba@suse.com>
- Clean-up the spec file
- Removed patch:
  * commons-cli-1.4-jdk9.patch
    + not needed since we are not building with maven
- Added patch:
  * CLI-253-workaround.patch
    + [CLI-253] Prevent "Unrecognized option: --null" when handling
  long opts in PosixParser
* Tue Oct 23 2018 Fridrich Strba <fstrba@suse.com>
- Upgrade to version 1.4
- Modify the build.xml.tar.bz2 to build with source/target 8 and
  adapt for the commons-cli-1.4
- Modified patch:
  * commons-cli-1.2-jdk9.patch -> commons-cli-1.4-jdk9.patch
    + Rediff the remaining hunk to the changed context of pom.xml
* Tue May 15 2018 fstrba@suse.com
- Modified patch:
  * commons-cli-1.2-jdk9.patch
    + Build with source and target 8 to prepare for a possible
    removal of 1.6 compatibility
- Run fdupes on the documentation
* Fri Sep 29 2017 fstrba@suse.com
- Don't condition the maven defines on release version, but on
  _maven_repository being defined
* Thu Sep 14 2017 fstrba@suse.com
- Added patch:
  * commons-cli-1.2-jdk9.patch
  - Specify java source and target level 1.6 in order to allow
    building with jdk9
* Fri May 19 2017 tchvatal@suse.com
- Fix build with new javapackages-tools
* Wed Mar 18 2015 tchvatal@suse.com
- Fix build with new javapackages-tools
* Thu Dec  4 2014 p.drouand@gmail.com
- Remove java-devel dependency; not needed anymore
* Fri Jun 27 2014 tchvatal@suse.com
- Fix the pom providing on 13.2
* Sat Mar  8 2014 badshah400@gmail.com
- For openSUSE >= 13.1 remove all references to maven scripts as
  these do not work; fixes building for openSUSE >= 13.1
- Lots of specfile formatting cleanups
- Move old %%changelog section entries to .changes with proper
  formatting
- Add copyright info to spec file.
* Mon Dec 12 2011 dmacvicar@suse.de
- rename apache-cli to apache-commons-cli
- add java() provides
* Tue Jul 19 2011 dmacvicar@suse.de
- converted to build with ant:ant
- removed reference to non existing target/osgi/MANIFEST
  in maven-build.xml
* Tue Nov  9 2010 chris.spike@arcor.de
- Removed maven* BRs in favour of apache-commons-parent
- Added deprecated groupId to depmap for compatibility reasons
* Mon Oct 18 2010 chris.spike@arcor.de
- Removed Epoch
* Sun Oct  3 2010 chris.spike@arcor.de
- Rename and rebase from jakarta-commons-cli
