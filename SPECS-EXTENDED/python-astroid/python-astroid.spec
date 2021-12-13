Vendor:         Microsoft Corporation
Distribution:   Mariner
# Remove when globs in setup.py work.
%{?python_disable_dependency_generator}

%global github_owner    PyCQA
%global github_name     astroid
%global commit ace7b2967ea762ec43fc7be8ab9c8007564d9be2
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           python-astroid
Version:        2.3.3
Release:        8%{?dist}
Summary:        Common base representation of python source code for pylint and other projects
License:        GPLv2+
URL:            https://github.com/%{github_owner}/%{github_name}
Source0:        https://github.com/PyCQA/astroid/archive/%{commit}/astroid-%{shortcommit}.tar.gz#/python-astroid-%{shortcommit}.tar.gz
Patch0:         noglobs.patch

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-lazy-object-proxy
BuildRequires:  python3-pytest
BuildRequires:  python3-pytest-runner
BuildRequires:  python3-six
BuildRequires:  python3-typed_ast >= 1.3.0
BuildRequires:  python3-wrapt
BuildRequires:  git-core

%global _description %{expand:
The aim of this module is to provide a common base representation of python
source code for projects such as pychecker, pyreverse, pylint...
It provides a compatible representation which comes from the _ast module. It
rebuilds the tree generated by the builtin _ast module by recursively walking
down the AST and building an extended ast. The new node classes have additional
methods and attributes for different usages. They include some support for
static inference and local name scopes. Furthermore, astroid builds partial
trees by inspecting living objects.}

%description %_description

%package -n python3-%{github_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{github_name}}
Requires:  python3-lazy-object-proxy
Requires:  python3-wrapt
Requires:  python3-typed_ast
Requires:  python3-six

%description -n python3-%{github_name} %_description

%prep
%autosetup -n astroid-%{commit} -p0
sed -i /six/d tox.ini
sed -i /six/d astroid/__pkginfo__.py

%build
%py3_build


%install
%py3_install
rm -rf %{buildroot}%{python3_sitelib}/astroid/tests


#%check
#%{__python3} -m pytest -v


%files -n python3-%{github_name}
%doc README.rst
%license COPYING
%{python3_sitelib}/astroid
%{python3_sitelib}/astroid*.egg-info

%changelog
* Thu Oct 14 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 2.3.3-8
- Initial CBL-Mariner import from Fedora 32 (license: MIT).
- Converting the 'Release' tag to the '[number].[distribution]' format.

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.3-7.gitace7b29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Jan 17 2020 Gwyn Ciesla <gwync@protonmail.com> - 2.3.3-6.gitace7b29
- Drop *s

* Fri Jan 17 2020 Gwyn Ciesla <gwync@protonmail.com> - 2.3.3-5.gitace7b29
- Drop tilded six deps.

* Wed Jan 08 2020 Gwyn Ciesla <gwync@protonmail.com> - 2.3.3-4.gitace7b29
- Require six

* Tue Jan 07 2020 Gwyn Ciesla <gwync@protonmail.com> - 2.3.3-3.gitace7b29
- Require typed_ast

* Thu Dec 12 2019 Gwyn Ciesla <gwync@protonmail.com> - 2.3.3-2.gitace7b29
- Disable dependency generator.

* Wed Nov 06 2019 Gwyn Ciesla <gwync@protonmail.com> - 2.3.3-1.gitace7b29
- 2.3.3

* Sun Oct 20 2019 Gwyn Ciesla <gwync@protonmail.com> - 2.3.2-1.git8b0fcc2
- 2.3.2

* Fri Oct 04 2019 Gwyn Ciesla <gwync@protonmail.com> - 2.3.1-3.gitbff51e9
- Really fix them.

* Fri Oct 04 2019 Gwyn Ciesla <gwync@protonmail.com> - 2.3.1-2.gitbff51e9
- Fix requires, BZ 1758430.

* Mon Sep 30 2019 Gwyn Ciesla <gwync@protonmail.com> - 2.3.1-1.gitbff51e9
- 2.3.1

* Tue Sep 24 2019 Gwyn Ciesla <gwync@protonmail.com> - 2.3.0-1.gitff97852
- 2.3.0.

* Sat Aug 17 2019 Miro Hrončok <mhroncok@redhat.com> - 2.2.5-5.git28fc86f
- Rebuilt for Python 3.8

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.5-4.git28fc86f
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Jul 12 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.2.5-3.git28fc86f
- Pull in the latest upstream snapshot with pytohn3.8 fixes (#1717653)

* Thu Apr 04 2019 Christian Dersch <lupinix@mailbox.org> - 2.2.5-2
- New BuildRequires: python3-typed_ast

* Sat Mar 30 2019 Christian Dersch <lupinix@fedoraproject.org> - 2.2.5-1
- new version

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Oct 02 2018 Christian Dersch <lupinix@fedoraproject.org> - 2.0.4-1
- new version

* Wed Aug 01 2018 Christian Dersch <lupinix@mailbox.org> - 2.0.2-1
- new version

* Wed Jul 25 2018 Christian Dersch <lupinix.fedora@gmail.com> - 2.0.1-1
- new version

* Sun Jul 15 2018 Christian Dersch <lupinix@fedoraproject.org> - 2.0.0-1
- Final version 2.0

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-0.5dev3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 29 2018 Miro Hrončok <mhroncok@redhat.com> - 2.0.0-0.4dev3
- Update to dev3

* Mon Jun 18 2018 Miro Hrončok <mhroncok@redhat.com> - 2.0.0-0.3dev1
- Rebuilt for Python 3.7

* Mon Jun 04 2018 Miro Hrončok <mhroncok@redhat.com> - 2.0.0-0.2dev1
- Update to 2.0.0dev1

* Mon May 21 2018 Miro Hrončok <mhroncok@redhat.com> - 2.0.0-0.1dev0
- Update to 2.0.0dev0
- Drop python2-astroid (that goes to it's own package in 1.6.x)
- Switch to pytest as does upstream

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jun 19 2017 Christian Dersch <lupinix@mailbox.org> - 1.5.3-1
- new version

* Mon May 29 2017 Christian Dersch <lupinix@mailbox.org> - 1.5.2-4
- Python 2 test fails also on F26 (I guess we need new enum34 there too)

* Mon May 29 2017 Christian Dersch <lupinix@mailbox.org> - 1.5.2-3
- add requirement on python-enum34 for Python 2

* Mon May 15 2017 Christian Dersch <lupinix@mailbox.org> - 1.5.2-2
- use correct github commit
- adjusted requirements, we need backports-functools_lru_cache now

* Sun May 14 2017 Christian Dersch <lupinix@mailbox.org> - 1.5.2-1
- new version

* Thu Mar 9 2017 Orion Poplawski <orion@cora.nwra.com> - 1.4.9-3
- Minor cleanup

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Dec 21 2016 Adam Williamson <awilliam@redhat.com> - 1.4.9-1
- New release 1.4.9
- Backport a patch from master branch to fix Python 3.6 compatibility
- Modernize spec file somewhat
- Rename python2 package
- Enable tests

* Wed Dec 14 2016 Charalampos Stratakis <cstratak@redhat.com> - 1.4.8-1
- Upstream 1.4.8

* Mon Dec 12 2016 Charalampos Stratakis <cstratak@redhat.com> - 1.4.5-4
- Rebuild for Python 3.6

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.5-3
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Wed Apr 27 2016 Brian C. Lane <bcl@redhat.com> - 1.4.5-2
- Ignore PyGIWarning (#1330651)
  Upstream PR https://github.com/PyCQA/astroid/pull/333

* Thu Apr 07 2016 Brian C. Lane <bcl@redhat.com> 1.4.5-1
- Upstream 1.4.5

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jan 18 2016 Brian C. Lane <bcl@redhat.com> 1.4.4-1
- Upstream 1.4.4

* Mon Jan 04 2016 Brian C. Lane <bcl@redhat.com> 1.4.3-1
- Upstream 1.4.3
- Drop included patches
- Drop running iconv on README.rst

* Fri Dec 11 2015 Brian C. Lane <bcl@redhat.com> 1.4.1-2
- Check for flags/enum types before checking for int
  Upstream PR https://github.com/PyCQA/astroid/pull/287

* Thu Dec 10 2015 Brian C. Lane <bcl@redhat.com> 1.4.1-1
- Upstream 1.4.1
- Drop included patches
- Drop requirement on logilab-common
- Add requirement on python-wrapt and python-lazy-object-proxy
- New upstream source from GitHub
- UnicodeEncodeError in AsStringVisitor.visit_functiondef
  https://bitbucket.org/logilab/astroid/issues/273/regression-unicodeencodeerror-in
- Remove %%check section, the full tox tests cannot be run because of un-packaged requirements

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.7-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Thu Jul 30 2015 Brian C. Lane <bcl@redhat.com> 1.3.7-1
- Upstream 1.3.7
- Fix for subprocess communicate() timeout argument
  https://bitbucket.org/logilab/astroid/pull-requests/83
- Fix for logilab-common required version in astroid

* Tue Jul 14 2015 Brian C. Lane <bcl@redhat.com> 1.3.6-5
- Fixes for gi.require_version from dshea
  https://bitbucket.org/logilab/astroid/pull-request/78

* Tue Jul 07 2015 Brian C. Lane <bcl@redhat.com> 1.3.6-4
- Helps if you actually APPLY the patch in question.

* Tue Jul 07 2015 Brian C. Lane <bcl@redhat.com> 1.3.6-3
- Fix for pygi deprecation warnings
  https://bitbucket.org/logilab/astroid/issue/86

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Apr 28 2015 Brian C. Lane <bcl@redhat.com> 1.3.6-1
- Upstream v1.3.6
- Fix for python3.4 multiprocessing
  https://bitbucket.org/logilab/pylint/issue/265/

* Thu Jan 29 2015 Brian C. Lane <bcl@redhat.com> 1.3.4-2
- Adjust paths for tests

* Wed Jan 28 2015 Brian C. Lane <bcl@redhat.com> 1.3.4-1
- Upstream v1.3.4
  Drop patches now included in upstream

* Fri Oct 17 2014 Brian C. Lane <bcl@redhat.com> 1.2.1-2
- Add patch to fix GLib detection (#1141440)
  https://bitbucket.org/logilab/astroid/issue/49

* Fri Oct 03 2014 Brian C. Lane <bcl@redhat.com> 1.2.1-1
- Upstream v1.2.1
  Drop patches now included in upstream

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 14 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.1-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Wed Apr 23 2014 Brian C. Lane <bcl@redhat.com> 1.1-3
- Add patch to fix metaclass recursion (upstream bug #25)
  https://bitbucket.org/logilab/astroid/issue/25/runtimeerror-maximum-recursion-depth

* Tue Apr 22 2014 Brian C. Lane <bcl@redhat.com> 1.1-2
- Add missing source file

* Tue Apr 22 2014 Brian C. Lane <bcl@redhat.com> 1.1-1
- Upstream v1.1
  Drop patches now included in upstream

* Tue Apr 01 2014 Cole Robinson <crobinso@redhat.com> - 1.0.1-3
- Fix some gobject introspection false positives (bz #1079643)

* Fri Feb 28 2014 Brian C. Lane <bcl@redhat.com> 1.0.1-2
- Add patch to fix gobject introspection of illegal symbol names (dshea)

* Thu Feb 27 2014 Brian C. Lane <bcl@redhat.com> 1.0.1-1
- Upstream v1.0.1
  Drop patch included in upstream

* Thu Oct 24 2013 Brian C. Lane <bcl@redhat.com> 1.0.0-6
- Switching on python3 support

* Tue Sep 17 2013 Brian C. Lane <bcl@redhat.com> 1.0.0-5
- Switch to versioned obsolete. (#996780)

* Fri Sep 13 2013 Brian C. Lane <bcl@redhat.com> 1.0.0-4
- Fix wrong obsoletes. Should be python-logilab-astng (#1007916)

* Tue Sep 03 2013 Brian C. Lane <bcl@redhat.com> 1.0.0-3
- Add upstream patch for TypeError bug

* Fri Aug 16 2013 Brian C. Lane <bcl@redhat.com> 1.0.0-2
- Removed BuildRoot from spec

* Tue Aug 13 2013 Brian C. Lane <bcl@redhat.com> 1.0.0-1
- Rename package to python-astroid
- Upstream v1.0.0 

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.24.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.24.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jan 10 2013 Brian C. Lane <bcl@redhat.com> 0.24.1-1
- Upstream v0.24.1
- Add python3-logilab-astng subpackage to spec. Not ready to turn it on yet
  due to this upstream bug: http://www.logilab.org/ticket/110213

* Fri Aug 03 2012 Brian C. Lane <bcl@redhat.com> 0.24.0-1
- Upstream v0.24.0

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.23.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Mar 14 2012 Brian C. Lane <bcl@redhat.com> 0.23.1-1
- Upstream v0.23.1

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.23.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Nov 18 2011 Brian C. Lane <bcl@redhat.com> - 0.23.0-1
- Upstream v0.23.0

* Fri Jul 29 2011 Brian C. Lane <bcl@redhat.com> - 0.22.0-1
- Upstream v0.22.0

* Mon Mar 28 2011 Brian C. Lane <bcl@redhat.com> - 0.21.1-1
- Upstream 0.21.1
- Add unit tests to spec

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Dec 06 2010 Brian C. Lane <bcl@redhat.com> - 0.21.0-2
- Add version to requirement for python-logilab-common so that updates will
  work correctly.

* Mon Nov 29 2010 Brian C. Lane <bcl@redhat.com> - 0.21.0-1
- Upstream 0.21.0

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 0.20.1-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Thu Jul 08 2010 Brian C. Lane <bcl@redhat.com> - 0.20.1-1
- Upstream 0.20.1

* Thu Mar 25 2010 Brian C. Lane <bcl@redhat.com> - 0.20.0-2
- Added python-setuptools to BuildRequires

* Thu Mar 25 2010 Brian C. Lane <bcl@redhat.com> - 0.20.0-1
- Upstream 0.20.0

* Sun Aug 30 2009 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.19.1-1
- Upstream 0.19.1 (bugfixes)

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.19.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jun 17 2009 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.19.0-1
- Upstream 0.19.0
- Fixes for better support of python 2.5 and 2.6

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.17.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Dec 27 2008 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.17.4-1
- Upstream 0.17.4

* Thu Jan 17 2008 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.17.2-1
- Upstream 0.17.2
- Package .egg-info file

* Mon Dec 24 2007 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.17.1-1
- Upstream 0.17.1
- Adjust license to a more specific GPLv2+
- Fix docs to be valid utf-8

* Sun Apr 01 2007 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.17.0-1
- Upstream 0.17.0

* Sun Dec 17 2006 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.16.3-1
- Upstream 0.16.3

* Tue Sep 26 2006 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.16.1-2
- Setting Provides/Obsoletes as per guidelines.

* Tue Sep 26 2006 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.16.1-1
- Renaming package python-logilab-astng from python-astng. Should have done
  a while ago.
- Upstream version 0.16.1

* Mon May 01 2006 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.16.0-0
- Version 0.16.0

* Sun Mar 12 2006 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.15.1-1
- Version 0.15.1

* Thu Jan 12 2006 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.14.0-1
- Version 0.14.0
- Drop the modname patch

* Tue Nov 15 2005 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.13.1-2
- Patch for the modname traceback

* Sat Nov 12 2005 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.13.1-1
- Fedora Extras import
- Disttagging

* Mon Nov 07 2005 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.13.1-0.1
- Version 0.13.1
- Remove our own GPL license text, since it's now included.

* Sun Nov 06 2005 Konstantin Ryabitsev <icon@fedoraproject.org> - 0.13.0-0.1
- Initial packaging.
