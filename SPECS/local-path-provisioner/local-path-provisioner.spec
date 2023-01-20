Summary:        Provides a way for the Kubernetes users to utilize the local storage in each node
Name:           local-path-provisioner
Version:        0.0.21
Release:        4%{?dist}
License:        ASL 2.0
URL:            https://github.com/rancher/local-path-provisioner
Group:          Applications/Text
Vendor:         Microsoft
Distribution:   Mariner
Source0:        https://github.com/rancher/%{name}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
#Note that the source file should be renamed to the format {name}-%{version}.tar.gz

BuildRequires: golang

%description
Provides a way for the Kubernetes users to utilize the local storage in each node. 

%prep
%setup -q

%build
export CGO_ENABLED=0
go build -mod=vendor 

%install
install -d %{buildroot}%{_bindir}
install local-path-provisioner %{buildroot}%{_bindir}/local-path-provisioner

%files
%{_bindir}/local-path-provisioner

%changelog
* Wed Jan 18 2023 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 0.0.21-4
- Bump release to rebuild with go 1.19.4

* Fri Dec 16 2022 Daniel McIlvaney <damcilva@microsoft.com> - 0.0.21-3
- Bump release to rebuild with go 1.18.8 with patch for CVE-2022-41717

* Tue Nov 01 2022 Olivia Crain <oliviacrain@microsoft.com> - 0.0.21-2
- Bump release to rebuild with go 1.18.8

* Thu Jun 23 2022 Lior Lustgarten <lilustga@microsoft.com> 0.0.21-1
- Original version for CBL-Mariner
- License Verified
