Summary:        A core cryptographic library written by Microsoft
Name:           SymCrypt
Version:        101.0.0
Release:        1%{?dist}
License:        MIT License
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System/Libraries
URL:            https://github.com/microsoft/SymCrypt
#Source0:       https://github.com/microsoft/SymCrypt/archive/v%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz
#Source1        https://github.com/smuellerDD/jitterentropy-library/archive/v3.3.1.tar.gz
Source1:        jitterentropy-library-3.3.1.tar.gz
%define debug_package %{nil}
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  python3-pyelftools

%description
A core cryptographic library written by Microsoft

# Only x86_64 and aarch64 are currently supported
%ifarch x86_64
%define symcrypt_arch AMD64
%endif

%ifarch aarch64
%define symcrypt_arch ARM64
%endif

%prep
%setup -q
%setup -q -a 1
# Create a symbolic link as if jitterentropy-library has been pulled in as git submodule
rm -rf jitterentropy-library
ln -s jitterentropy-library-3.3.1 jitterentropy-library

%build
mkdir bin; cd bin

cmake   .. \
        -DCMAKE_TOOLCHAIN_FILE="../cmake-toolchain/LinuxUserMode-%{symcrypt_arch}.cmake" \
        -DCMAKE_BUILD_TYPE=Release

cmake --build .

%install
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_includedir}
install inc/symcrypt* %{buildroot}%{_includedir}
# Use cp -P to preserve symbolic links
cp -P bin/module/%{symcrypt_arch}/LinuxUserMode/generic/libsymcrypt.so* %{buildroot}%{_libdir}
chmod 755 %{buildroot}%{_libdir}/libsymcrypt.so.%{version}

%files
%license LICENSE
%license NOTICE
%{_libdir}/libsymcrypt.so*
%{_includedir}/*

%changelog
* Mon Feb 14 2022 Samuel Lee <saml@microsoft.com> - 101.0.0-1
- Initial CBL-Mariner import
