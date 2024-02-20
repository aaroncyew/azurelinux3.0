# Disabled debuginfo package as the autogenerated 'debugfiles.list' file is empty.
# In other words there were no debug symbols to package.
%global debug_package %{nil}
%global gem_name console
Summary:        Logging for Ruby
Name:           rubygem-console
Version:        1.23.3
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Azure Linux
Group:          Development/Languages
URL:            https://socketry.github.io/console/
Source0:        https://github.com/socketry/console/archive/refs/tags/v%{version}.tar.gz#/%{gem_name}-%{version}.tar.gz
BuildRequires:  ruby
Requires:       rubygem-fiber-local
Provides:       rubygem(%{gem_name}) = %{version}-%{release}

%description
Provides console logging for Ruby applications.
Implements fast, buffered log output.

%prep
%setup -q -n %{gem_name}-%{version}
%gemspec_clear_signing

%build
gem build %{gem_name}

%install
gem install -V --local --force --install-dir %{buildroot}/%{gemdir} %{gem_name}-%{version}.gem

%files
%defattr(-,root,root,-)
%{gemdir}

%changelog
* Tue Jan 30 2024 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 1.23.3-1
- Auto-upgrade to 1.23.3 - Azure Linux 3.0 - package upgrades.
- Removed gem signing.

* Tue Jul 19 2022 Neha Agarwal <nehaagarwal@microsoft.com> - 1.10.1-3
- Add provides.

* Tue Mar 22 2022 Neha Agarwal <nehaagarwal@microsoft.com> - 1.10.1-2
- Build from .tar.gz source.

* Wed Jan 06 2021 Henry Li <lihl@microsoft.com> - 1.10.1-1
- License verified
- Original version for CBL-Mariner
