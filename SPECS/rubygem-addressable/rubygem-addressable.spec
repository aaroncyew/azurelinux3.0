%global debug_package %{nil}
%global gemdir %(IFS=: R=($(gem env gempath)); echo ${R[${#R[@]}-1]})
%global gem_name addressable
Summary:        an alternative implementation to the URI implementation that is part of Ruby's standard library
Name:           rubygem-addressable
Version:        2.7.0
Release:        2%{?dist}
License:        Apache 2.0
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Development/Languages
URL:            https://rubygems.org/gems/%{gem_name}/versions/%{version}
Source0:        https://rubygems.org/downloads/%{gem_name}-%{version}.gem
Patch0: CVE-2021-32740.patch
BuildRequires:  ruby
Requires:       rubygem-public_suffix < 5.0

%description
Addressable is an alternative implementation to the URI implementation that is
part of Ruby's standard library. It offers heuristic parsing, and additionally
provides extensive support for IRIs and URI templates.

%prep
%autosetup -c -T

%build

%install
gem install -V --local --force --install-dir %{buildroot}/%{gemdir} %{SOURCE0}

%files
%defattr(-,root,root,-)
%license %{gemdir}/gems/%{gem_name}-%{version}/LICENSE.txt
%{gemdir}

%changelog
*   Fri Jul 30 2021 Mariner Autopatcher <cblmargh@microsoft.com> 2.7.0-2
-   Added patch file(s) CVE-2021-32740.patch
* Mon Jan 04 2021 Henry Li <lihl@microsoft.com> - 2.7.0-1
- License verified
- Original version for CBL-Mariner
