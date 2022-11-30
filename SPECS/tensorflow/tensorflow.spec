Summary:        TensorFlow is an open source machine learning framework for everyone.
Name:           tensorflow
Version:        2.8.3
Release:        1%{?dist}
License:        #####
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          Development/Languages/Python
URL:            https://www.tensorflow.org/
Source0:        https://github.com/tensorflow/tensorflow/archive/refs/tags/v%{Version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-cache.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  build-essential
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-requests
BuildRequires:  python3-packaging
BuildRequires:  python3-wheel
BuildRequires:  python3-numpy
BuildRequires:  bazel = 4.2.1
BuildRequires:  binutils
BuildRequires:  which
BuildRequires:  tar
BuildRequires:  git
BuildRequires:  python3-pip
BuildRequires:  libstdc++-devel


%description
TensorFlow is an open source machine learning framework for everyone.

%package -n     python3-tensorflow
Summary:        python-tensorflow
Requires:       python3-devel
Requires:       python3-absl-py
Requires:       python3-astunparse
Requires:       python3-flatbuffers
Requires:       python3-gast
Requires:       python3-libclang
Requires:       python3-h5py
Requires:       python3-numpy = 1.22.3
Requires:       python3-opt-einsum
Requires:       python3-protobuf 
Requires:       python3-six
Requires:       python3-termcolor
Requires:       python3-typing-extensions
Requires:       python3-wrapt
Requires:       python3-grpcio
Requires:       python3-MarkupSafe
Requires:       python3-cachetools
Requires:       python3-google-auth
Requires:       python3-google-auth-oauthlib
Requires:       python3-importlib-metadata
Requires:       python3-markdown
Requires:       python3-oauthlib
Requires:       python3-pyasn1-modules
Requires:       python3-requests-oauthlib
Requires:       python3-rsa
Requires:       python3-werkzeug
Requires:       python3-zipp
Requires:       python3-pyasn1
Requires:       python3-charset_normalizer
Requires:       python3-idna

%description -n python3-tensorflow
Python 3 version.

%prep
%autosetup -p1


%build
tar -xf %{SOURCE1} -C /root/

ln -s /usr/bin/python3 /usr/bin/python

bazel --batch build  --verbose_explanations //tensorflow/tools/pip_package:build_pip_package
# ---------
# steps to create the cache tar. Need to have network to create the cache. 
#----------------------------------
# pushd /root
# tar -czvf cacheroot.tar.gz .cache  #creating the cache using the /root/.cache directory
# popd
# mv /root/cacheroot.tar.gz /usr/ 

./bazel-bin/tensorflow/tools/pip_package/build_pip_package pyproject-wheeldir/
# --------


%install
%pyproject_install


 
%check
pip3 install nose pytest==7.1.3 
mkdir -pv test
cd test
#PYTHONPATH=%{buildroot}%{python3_sitelib} PATH=$PATH:%{buildroot}%{_bindir} %python3 -c "import numpy; numpy.test()"

%files -n python3-tensorflow
%license LICENSE
%{python3_sitelib}/*
%{_bindir}/estimator_ckpt_converter
%{_bindir}/import_pb_to_tensorboard
%{_bindir}/saved_model_cli
%{_bindir}/tensorboard
%{_bindir}/tf_upgrade_v2
%{_bindir}/tflite_convert
%{_bindir}/toco
%{_bindir}/toco_from_protos


%changelog
* Thu Sep 22 2022 Riken Maharjan <rmaharjan@microsoft> - 2.8.3-1
- License verified
- Original version for CBL-Mariner
