Summary:        The KeysInUse Engine for OpenSSL allows the logging of private key usage through OpenSSL
Name:           KeysInUse-OpenSSL
Version:        0.3.0
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System/Libraries
URL:            https://github.com/microsoft/KeysInUse-OpenSSL
#Source0:       https://github.com/microsoft/KeysInUse-OpenSSL/archive/v%{version}.tar.gz
Source0:        %{name}-%{version}.tar.gz
BuildRequires:  openssl-devel
BuildRequires:  golang >= 1.16.6
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  make
Requires:    openssl >= 1.1.1, openssl < 1.1.2

%description
 The KeysInUse Engine for OpenSSL allows the logging of private key usage through OpenSSL

%prep
%setup -q

%build
export GO111MODULE=off

cmake -DCMAKE_TOOLCHAIN_FILE=./cmake-toolchains/linux-amd64-glibc.cmake -H./ -B./build
cmake --build ./build --target keysinuse

cd ./packaging/util
make $(realpath ../../bin/keysinuseutil)

%define keysinuse_dir %{buildroot}/%{_libdir}/keysinuse/
%install
mkdir -p %{keysinuse_dir}
mkdir -p %{buildroot}/usr/bin/

cp ./bin/keysinuse.so %{keysinuse_dir}
cp ./bin/keysinuseutil %{buildroot}/usr/bin/

%files
%license LICENSE
%{_libdir}/keysinuse/keysinuse.so
/usr/bin/keysinuseutil

%pre
if [ -x /usr/bin/keysinuseutil ]; then
  echo "Disabling version $2 of keysinuse engine for OpenSSL"
  /usr/bin/keysinuseutil uninstall || echo "Failed to deconfigure old version"
fi

%post
if [ ! -e /var/log/keysinuse ]; then
  mkdir /var/log/keysinuse
fi
chown root:root /var/log/keysinuse
chmod 1733 /var/log/keysinuse

ln -s /usr/lib/keysinuse/keysinuse.so $(/usr/bin/openssl version -e | awk '{gsub(/"/, "", $2); print $2}')/keysinuse.so 

if [ -x /usr/bin/keysinuseutil ]; then
  echo "Enabling keysinuse engine for OpenSSL"
  /usr/bin/keysinuseutil install || echo "Configuring engine failed"
fi

%preun
if [ -x /usr/bin/keysinuseutil ]; then
  echo "Disabling keysinuse engine for OpenSSL"
  /usr/bin/keysinuseutil uninstall || echo "Deconfiguring keysinuse engine failed"
fi

engine_link=$(/usr/bin/openssl version -e | awk '{gsub(/"/, "", $2); print $2}')/keysinuse.so
if [ -e $engine_link ]; then
  rm $engine_link
fi

%changelog
* Mon May 23 2022 Maxwell Moyer-McKee <mamckee@microsoft.com> - 0.3.0-1
- Original version for CBL-Mariner