Name:           build-essential
Summary:        Metapackage to install all build tools
Version:        0.1
Release:        5%{?dist}
License:        GPLv2
Requires:       gcc, binutils, make, glibc-devel, kernel-headers, automake
Requires:       autoconf, libtool, gawk, diffutils, patch, bison, installkernel

%description
Metapackage to install all build tools

%prep

%build

%files
%defattr(-,root,root,0755)

%changelog
* Wed Mar 30 2020 Chris Co <chrco@microsoft.com> - 0.1-5
- Add installkernel
*   Thu Apr 30 2020 Emre Girgin <mrgirgin@microsoft.com> 0.1-4
-   Renaming linux-api-headers to kernel-headers.
-   Initial CBL-Mariner import from Photon (license: Apache2).
*   Fri Dec 07 2018 Srivatsa S. Bhat (VMware) <srivatsa@csail.mit.edu> 0.1-3
-   Add patch and bison
*   Thu Dec 15 2016 Alexey Makhalov <amakhalov@vmware.com> 0.1-2
-   Added diffutils
*   Fri Aug 5 2016 Dheeraj Shetty <dheerajs@vmware.com> 0.1-1
-   Initial
