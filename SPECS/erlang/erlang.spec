%define  debug_package %{nil}
%define  usr_local_bin %{_prefix}/local/bin
%define  usr_local_lib %{_prefix}/local/lib
Summary:        erlang
Name:           erlang
Version:        25.2
Release:        1%{?dist}
License:        ASL 2.0
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Development/Languages
URL:            https://erlang.org
Source0:        https://github.com/erlang/otp/archive/OTP-%{version}/otp-OTP-%{version}.tar.gz
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  unixODBC-devel
BuildRequires:  unzip

%description
erlang programming language

%prep
%setup -q -n otp-OTP-%{version}

%build
export ERL_TOP=`pwd`
./configure
make

%install

%make_install

%post

%files
%defattr(-,root,root)
%license LICENSE.txt
%{usr_local_bin}/ct_run
%{usr_local_bin}/dialyzer
%{usr_local_bin}/epmd
%{usr_local_bin}/erl
%{usr_local_bin}/erlc
%{usr_local_bin}/escript
%{usr_local_bin}/run_erl
%{usr_local_bin}/to_erl
%{usr_local_bin}/typer
%{usr_local_lib}/erlang/*

%changelog
* Tue Feb 14 2023 Sam Meluch <sammeluch@microsoft.com> - 25.2-1
- Update to version 25.2

* Wed Jan 19 2022 Cameron Baird <cameronbaird@microsoft.com> - 24.2-1
- Update to version 24.2

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 22.0.7-2
- Added %%license line automatically

* Thu Mar 19 2020 Henry Beberman <henry.beberman@microsoft.com> 22.0.7-1
- Update to 22.0.7. Fix URL. Fix Source0 URL. License verified.

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 19.3-4
- Initial CBL-Mariner import from Photon (license: Apache2).

* Thu Jan 31 2019 Siju Maliakkal <smaliakkal@vmware.com> 19.3-3
- Revert to old version to fix rabbitmq-server startup failure

* Fri Dec 07 2018 Ashwin H <ashwinh@vmware.com> 21.1.4-1
- Update to version 21.1.4

* Mon Sep 24 2018 Dweep Advani <dadvani@vmware.com> 21.0-1
- Update to version 21.0

* Fri Oct 13 2017 Alexey Makhalov <amakhalov@vmware.com> 19.3-2
- Remove BuildArch

* Thu Apr 06 2017 Chang Lee <changlee@vmware.com> 19.3-1
- Updated Version

* Mon Dec 12 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 19.1-1
- Initial.
