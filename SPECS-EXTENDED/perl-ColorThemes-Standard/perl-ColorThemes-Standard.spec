Vendor:         Microsoft Corporation
Distribution:   Mariner
Name:           perl-ColorThemes-Standard
Version:        0.003
Release:        2%{?dist}
Summary:        Standard collection of generic color themes
License:        GPL+ or Artistic
URL:            https://metacpan.org/release/ColorThemes-Standard/
Source0:        https://cpan.metacpan.org/authors/id/P/PE/PERLANCAR/ColorThemes-Standard-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  coreutils
BuildRequires:  make
BuildRequires:  perl-generators
BuildRequires:  perl-interpreter
BuildRequires:  perl(ExtUtils::MakeMaker) >= 6.76
BuildRequires:  perl(strict)
BuildRequires:  perl(warnings)
# Run-time
BuildRequires:  perl(ColorThemeBase::Static::FromStructColors) >= 0.006
BuildRequires:  perl(parent)
# Tests
BuildRequires:  perl(blib)
BuildRequires:  perl(File::Spec)
BuildRequires:  perl(IO::Handle)
BuildRequires:  perl(IPC::Open3)
BuildRequires:  perl(Test::More)
Requires:       perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))
Requires:       perl(ColorThemeBase::Static::FromStructColors) >= 0.006

%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}^perl\\((ColorThemeBase::Static::FromStructColors)\\)\s*$

%description
This module contains a standard collection of generic color themes.

%prep
%setup -q -n ColorThemes-Standard-%{version}

%build
perl Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1 NO_PERLLOCAL=1
%{make_build}

%install
%{make_install}
%{_fixperms} $RPM_BUILD_ROOT/*

%check
unset AUTHOR_TESTING
make test

%files
%license LICENSE
%doc Changes README
%{perl_vendorlib}/*
%{_mandir}/man3/*

%changelog
* Wed Jan 26 2022 Pawel Winogrodzki <pawelwi@microsoft.com> - 0.003-2
- Initial CBL-Mariner import from Fedora 36 (license: MIT).

* Mon Nov 29 2021 Jitka Plesnikova <jplesnik@redhat.com> 0.003-1
- Specfile autogenerated by cpanspec 1.78.
