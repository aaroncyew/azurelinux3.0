Vendor:         Microsoft Corporation
Distribution:   Azure Linux
Name:           perl-Net-LibIDN2
Version:        1.01
Release:        3%{?dist}
Summary:        Perl binding for GNU Libidn2
License:        GPL+ or Artistic
URL:            https://metacpan.org/release/Net-LibIDN2
Source0:        https://cpan.metacpan.org/authors/id/T/TH/THOR/Net-LibIDN2-%{version}.tar.gz#/perl-Net-LibIDN2-%{version}.tar.gz
BuildRequires:  coreutils
BuildRequires:  findutils
BuildRequires:  gcc
BuildRequires:  libidn2-devel >= 2.0.0
BuildRequires:  perl-devel
BuildRequires:  perl-generators
BuildRequires:  perl-interpreter
BuildRequires:  perl(Devel::CheckLib)
BuildRequires:  perl(ExtUtils::CBuilder)
BuildRequires:  perl(lib)
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(strict)
BuildRequires:  perl(warnings)
# Run-time:
BuildRequires:  perl(:VERSION) >= 5.6
BuildRequires:  perl(DynaLoader)
BuildRequires:  perl(Exporter)
# Tests:
BuildRequires:  perl(Encode)
BuildRequires:  perl(Test::More) >= 0.10
# Optional tests:
BuildRequires:  perl(POSIX)
Requires:       perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))

%description
This Perl module provides bindings for GNU Libidn2, a C library for handling
internationalized domain names according to IDNA 2008 (RFC 5890, RFC 5891,
RFC 5892, RFC 5893).

%prep
%setup -q -n Net-LibIDN2-%{version}
# Remove bundled modules
rm -rf inc
perl -i -ne 'print $_ unless m{^inc/}' MANIFEST

%build
perl Build.PL installdirs=vendor optimize="$RPM_OPT_FLAGS"
./Build

%install
./Build install destdir=$RPM_BUILD_ROOT create_packlist=0
find $RPM_BUILD_ROOT -type f -name '*.bs' -size 0 -delete
%{_fixperms} $RPM_BUILD_ROOT/*

%check
./Build test

%files
%license LICENSE
%doc Changes README
%{perl_vendorarch}/auto/*
%{perl_vendorarch}/Net*
%{_mandir}/man3/*

%changelog
* Fri Jan 29 2021 Joe Schmitt <joschmit@microsoft.com> - 1.01-3
- Initial CBL-Mariner import from Fedora 32 (license: MIT).
- Remove optional glibc test dep

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.01-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Nov 11 2019 Petr Pisar <ppisar@redhat.com> - 1.01-1
- 1.01 bump

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.00-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri May 31 2019 Jitka Plesnikova <jplesnik@redhat.com> - 1.00-8
- Perl 5.30 rebuild

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.00-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.00-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 29 2018 Jitka Plesnikova <jplesnik@redhat.com> - 1.00-5
- Perl 5.28 rebuild

* Thu May 31 2018 Petr Pisar <ppisar@redhat.com> - 1.00-4
- Adapt to changes in libidn-2.0.5 (bug #1584611)

* Fri Mar 02 2018 Petr Pisar <ppisar@redhat.com> - 1.00-3
- Adapt to removing GCC from a build root (bug #1547165)

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.00-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Sep 26 2017 Petr Pisar <ppisar@redhat.com> - 1.00-1
- 1.00 bump

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.03-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.03-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jun 05 2017 Jitka Plesnikova <jplesnik@redhat.com> - 0.03-2
- Perl 5.26 rebuild

* Wed Apr 26 2017 Petr Pisar <ppisar@redhat.com> 0.03-1
- Specfile autogenerated by cpanspec 1.78.
