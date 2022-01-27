Vendor:         Microsoft Corporation
Distribution:   Mariner
Name:           perl-Regexp-Pattern-Perl
Version:        0.006
Release:        1%{?dist}
Summary:        Regexp patterns related to Perl
License:        GPL+ or Artistic
URL:            https://metacpan.org/release/Regexp-Pattern-Perl/
Source0:        https://cpan.metacpan.org/authors/id/P/PE/PERLANCAR/Regexp-Pattern-Perl-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  coreutils
BuildRequires:  make
BuildRequires:  perl-generators
BuildRequires:  perl-interpreter
BuildRequires:  perl(ExtUtils::MakeMaker) >= 6.76
BuildRequires:  perl(strict)
BuildRequires:  perl(warnings)
# Tests
BuildRequires:  perl(blib)
BuildRequires:  perl(File::Spec)
BuildRequires:  perl(IO::Handle)
BuildRequires:  perl(IPC::Open3)
BuildRequires:  perl(Test::More)
Requires:       perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))

%description
Regexp::Pattern is a convention for organizing reusable regex patterns.

%prep
%setup -q -n Regexp-Pattern-Perl-%{version}

%build
perl Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1 NO_PERLLOCAL=1
%{make_build}

%install
%{make_install}
%{_fixperms} $RPM_BUILD_ROOT/*

%check
unset AUTHOR_TESTING RELEASE_TESTING
make test

%files
%license LICENSE
%doc Changes README
%{perl_vendorlib}/*
%{_mandir}/man3/*

%changelog
* Mon Dec 20 2021 Jitka Plesnikova <jplesnik@redhat.com> - 0.006-1
- 0.006 bump

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.004-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri May 21 2021 Jitka Plesnikova <jplesnik@redhat.com> - 0.004-3
- Perl 5.34 rebuild

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.004-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Oct 02 2020 Jitka Plesnikova <jplesnik@redhat.com> - 0.004-1
- 0.004 bump

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.002-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jul 03 2020 Jitka Plesnikova <jplesnik@redhat.com> 0.002-1
- Specfile autogenerated by cpanspec 1.78.
