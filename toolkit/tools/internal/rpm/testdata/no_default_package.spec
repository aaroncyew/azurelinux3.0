Summary:        Test spec file with with no default package
Name:           no_default_package
Version:        1.0.0
Release:        1%{?dist}
License:        MIT
URL:            https://test.com
Group:          Test
Vendor:         Microsoft
Distribution:   Mariner

%description
Test spec. Make sure the default package is not built!

%package -n subpackage_name
Summary:        Actually built subpackage

%description -n subpackage_name
Test subpackage, which should be generate when this spec is built.

%prep

%build

%install

%files -n subpackage_name
%defattr(-,root,root)

%changelog
* Mon Nov 07 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0.0-1
- Initial creation.


