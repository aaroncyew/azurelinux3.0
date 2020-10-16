Summary:        Cross-platform path specification manipulation for Perl
Name:           perl-Path-Class
Version:        0.37
Release:        6%{?dist}
URL:            http://search.cpan.org/~kwilliams/Path-Class-0.37/
License:        The Perl 5 License (Artistic 1 & GPL 1)
Group:          Development/Libraries
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source:         http://search.cpan.org/CPAN/authors/id/K/KW/KWILLIAMS/Path-Class-%{version}.tar.gz
%define sha1    Path-Class=448cc1089add95d6a616a8e22adbde83dcb8f562

BuildArch:      noarch
BuildRequires:  perl >= 5.28.0

Requires:       perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))
Requires:       perl(File::Copy)
Requires:       perl(Perl::OSType)


%description
Path::Class is a module for manipulation of file and directory specifications (strings describing their locations, like '/home/ken/foo.txt' or 'C:\Windows\Foo.txt') in a cross-platform manner. It supports pretty much every platform Perl runs on, including Unix, Windows, Mac, VMS, Epoc, Cygwin, OS/2, and NetWare.

The well-known module File::Spec also provides this service, but it's sort of awkward to use well, so people sometimes avoid it, or use it in a way that won't actually work properly on platforms significantly different than the ones they've tested their code on.

%prep
%setup -q -n Path-Class-%{version}

%build
env PERL_MM_USE_DEFAULT=1 perl Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1 OPTIMIZE="%{optflags}"
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
find %{buildroot} -name 'perllocal.pod' -delete

%check
make test

%files
%license LICENSE
%{perl_vendorlib}/*
%{_mandir}/man?/*

%changelog
*   Mon Oct 12 2020 Joe Schmitt <joschmit@microsoft.com> 0.37-6
-   Use new perl package names.
-   Build with NO_PACKLIST option.
* Sat May 09 00:20:47 PST 2020 Nick Samson <nisamson@microsoft.com> - 0.37-5
- Added %%license line automatically

*   Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 0.37-4
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Fri Sep 21 2018 Dweep Advani <dadvani@vmware.com> 0.37-3
-   Consuming perl version upgrade of 5.28.0
*   Tue Apr 25 2017 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 0.37-2
-   Fix arch
*   Wed Apr 19 2017 Xiaolin Li <xiaolinl@vmware.com> 0.37-1
-   Initial version.
