Summary:        elixir
Name:           elixir
Version:        1.14.3
Release:        1%{?dist}
License:        Apache-2.0
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Development/Languages
URL:            https://elixir-lang.org
Source0:        https://github.com/elixir-lang/elixir/archive/v%{version}/elixir-%{version}.tar.gz
BuildRequires:  erlang
BuildRequires:  glibc-lang

%description
elixir programming language

%prep
%setup -q -n elixir-%{version}

%build
export LANG="en_US.UTF-8"
make

%install
%make_install

%post

%files


%changelog
* Mon Feb 27 2023 Sam Meluch <sammeluch@microsoft.com> - 1.14.3-1
- Add elixir v1.14.3 to Mariner.
