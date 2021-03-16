%global debug_package %{nil}

# shim takes in gnu-efi as a submodule.
%global gnuefiversion e32d8c84a5748a2e3b7220dae638418f81a7986d

Summary:        First stage UEFI bootloader
Name:           shim-unsigned-x64
Version:        15.3
Release:        1%{?dist}
URL:            https://github.com/rhboot/shim
License:        BSD
Vendor:         Microsoft
Distribution:   Mariner
Source0:        https://github.com/rhboot/shim/archive/shim-15.3-rc2.tar.gz
Source1:        https://github.com/rhboot/gnu-efi/archive/%{gnuefiversion}.tar.gz
Source100:      cbl-mariner-ca.der
ExclusiveArch:  x86_64

%description
shim is a trivial EFI application that, when run, attempts to open and
execute another application.
On systems with a TPM chip enabled and supported by the system firmware,
shim will extend various PCRs with the digests of the targets it is
loading.

%prep
%autosetup -n shim-shim-15.3-rc2 -p1
# Manually set up gnu-efi submodule
cp %{SOURCE1} gnu-efi-%{gnuefiversion}.tar.gz
tar -zxf gnu-efi-%{gnuefiversion}.tar.gz
pwd
ls
ls gnu-efi
rmdir gnu-efi
mv gnu-efi-%{gnuefiversion} gnu-efi
ls gnu-efi

%build
cp %{SOURCE100} cert.der
make shimx64.efi VENDOR_CERT_FILE=cert.der EFI_PATH=/usr/lib/gnuefi

%install
install -vdm 755 %{buildroot}/usr/share/%{name}
install -vm 644 shimx64.efi %{buildroot}/usr/share/%{name}/shimx64.efi

%files
%defattr(-,root,root)
%license COPYRIGHT
/usr/share/%{name}/shimx64.efi

%changelog
* Tue Mar 16 2021 Chris Co <chrco@microsoft.com> 15.3-1
- Update to 15.3
- Add gnu-efi source
- Remove extra patches. These are incorporated into latest version

* Tue Aug 25 2020 Chris Co <chrco@microsoft.com> 15-6
- Apply patch files (from CentOS: shim-15-8.el7)
* Wed Jul 29 2020 Chris Co <chrco@microsoft.com> 15-5
- Update built-in cert
* Mon Jun 22 2020 Chris Co <chrco@microsoft.com> 15-4
- Update install path
* Thu May 14 2020 Chris Co <chrco@microsoft.com> 15-3
- Update test key
* Mon May 04 2020 Emre Girgin <mrgirgin@microsoft.com> 15-2
- Replace BuildArch with ExclusiveArch
* Wed Apr 29 2020 Chris Co <chrco@microsoft.com> 15-1
- Original version for CBL-Mariner.