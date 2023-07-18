#!/bin/bash

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

set -e

script_dir=$( realpath "$(dirname "$0")" )
topdir=/usr/src/mariner
enable_local_repo=false

switch_to_red_text() {
    printf "\e[31m"
}

switch_to_normal_text() {
    printf "\e[0m"
}

print_error() {
    echo ""
    switch_to_red_text
    echo ">>>> ERROR: $1"
    switch_to_normal_text
    echo ""
}

help() {
echo "
Usage:
sudo make containerized-rpmbuild [REPO_PATH=/path/to/CBL-Mariner] [MODE=test|build] [VERSION=1.0|2.0] [MOUNTS= /src/path:/dst/path] [ENABLE_REPO=y]

Starts a docker container with the specified version of mariner.

Optional arguments:
    REPO_PATH:      path to the CBL-Mariner repo root directory. default: "current directory"
    MODE            build or test. default:"build"
                        In 'test' mode it will use a pre-built mariner chroot image.
                        In 'build' mode it will use the latest published container.
    VERISION        1.0 or 2.0. default: "2.0"
    MOUNTS          mount a directory into the container. Should be of the form '/src/dir:/dest/dir'. 
                    Can be specified multiple times.
    ENABLE_REPO:    Set to 'y' to use local RPMs to satisfy package dependencies. default: "n"

To see help, run 'sudo make containerized-rpmbuild-help'
"
}

build_chroot() {
    pushd "${repo_path}/toolkit"
    echo "Building worker chroot..."
    sudo make graph-cache REBUILD_TOOLS=y > /dev/null
    popd
}

build_tools() {
    pushd "${repo_path}/toolkit"
    echo "Building tools..."
    sudo make go-depsearch REBUILD_TOOLS=y > /dev/null
    sudo make go-grapher REBUILD_TOOLS=y > /dev/null
    sudo make go-specreader REBUILD_TOOLS=y > /dev/null
    popd
}

build_graph() {
    pushd "${repo_path}/toolkit"
    echo "Building dependency graph..."
    sudo make workplan > /dev/null
    popd
}

while (( "$#")); do
  case "$1" in
    -m ) mode="$2"; shift 2 ;;
    -v ) version="$2"; shift 2 ;;
    -p ) repo_path="$2"; shift 2 ;;
    --enable-local-repo ) enable_local_repo=true; shift ;;
    --help ) help; exit 1 ;;
    ? ) echo -e "ERROR: INVALID OPTION.\n\n"; help; exit 1 ;;
  esac
done

# Assign default values
[[ -z "${repo_path}" ]] && repo_path="$(dirname $0)" && repo_path=${repo_path%'/toolkit'*}
[[ ! -d "${repo_path}" ]] && { print_error " Directory ${repo_path} does not exist"; exit 1; }
[[ -z "${mode}" ]] && mode="build"
[[ -z  "${version}" ]] && version="2.0"

echo "Running in ${mode} mode, requires root..."
echo "Running as root!"

# ==================== Setup ====================
cd "${script_dir}"
build_dir="${script_dir}/build_container"
mkdir -p "${build_dir}"

# Get Mariner GitHub branch at $repo_path
pushd ${repo_path}
repo_branch=$(git rev-parse --abbrev-ref HEAD)
popd

#Set splash text based on mode
if [[ "${mode}" == "build" ]]; then
    splash_txt="builder_splash.txt"
else
    splash_txt="tester_splash.txt"
fi

# ============ Populate SRPMS ============
# Populate ${repo_path}/build/INTERMEDIATE_SRPMS with SRPMs, that can be used to build RPMs in the container
pushd "${repo_path}/toolkit"
echo "Populating Intermediate SRPMs..."
sudo make input-srpms SRPM_FILE_SIGNATURE_HANDLING="update" > /dev/null
popd

# ============ Map chroot mount ============
if [[ "${mode}" == "build" ]]; then
    # Create a new directory and map it to chroot directory in container
    if [ -d "${repo_path}/build/container-build" ]; then rm -Rf ${repo_path}/build/container-build; fi
    if [ -d "${repo_path}/build/container-buildroot" ]; then rm -Rf ${repo_path}/build/container-buildroot; fi
    mkdir ${repo_path}/build/container-build
    mkdir ${repo_path}/build/container-buildroot
    mounts="${mounts} ${repo_path}/build/container-build:${topdir}/BUILD ${repo_path}/build/container-buildroot:${topdir}/BUILDROOT"
fi

# ============ Setup tools ============
# Copy relavant build tool executables from ${repo_path}/tools/out
echo "Setting up tools..."
if [[ ( ! -f "${repo_path}/toolkit/out/tools/depsearch" ) || ( ! -f "${repo_path}/toolkit/out/tools/grapher" ) || ( ! -f "${repo_path}/toolkit/out/tools/specreader" ) ]]; then build_tools; fi
if [[ ! -f "${repo_path}/build/pkg_artifacts/graph.dot" ]]; then build_graph; fi
cp ${repo_path}/toolkit/out/tools/depsearch ${build_dir}/
cp ${repo_path}/toolkit/out/tools/grapher ${build_dir}/
cp ${repo_path}/toolkit/out/tools/specreader ${build_dir}/
cp ${repo_path}/build/pkg_artifacts/graph.dot ${build_dir}/

# ========= Setup mounts =========
cd "${script_dir}"
echo "Setting up mounts..."

mounts="${mounts} ${repo_path}/out/RPMS:/mnt/RPMS"
if [[ "${mode}" == "build" ]]; then
    # Add extra build mounts
    mounts="${mounts} ${repo_path}/build/INTERMEDIATE_SRPMS:/mnt/INTERMEDIATE_SRPMS ${repo_path}/SPECS:${topdir}/SPECS"
fi

rm -f ${build_dir}/mounts.txt
for mount in $mounts $extra_mounts; do
    if [[ -d "${mount%%:*}" ]]; then
        echo "${mount%%:*}' -> '${mount##*:}"  >> "${build_dir}/mounts.txt"
    else
        echo "WARNING: '${mount%%:*}' does not exist. Skipping mount."  >> "${build_dir}/mounts.txt"
        continue
    fi
    mount_arg=" $mount_arg -v '$mount' "
done

# ============ Build the dockerfile ============
dockerfile="${script_dir}/resources/mariner.Dockerfile"

if [[ "${mode}" == "build" ]]; then # Configure base image
    echo "Importing chroot into docker..."
    chroot_file="${repo_path}/build/worker/worker_chroot.tar.gz"
    if [[ ! -f "${chroot_file}" ]]; then build_chroot; fi
    chroot_hash=$(sha256sum "${chroot_file}" | cut -d' ' -f1)
    # Check if the chroot file's hash has changed since the last build
    if [[ ! -f "${script_dir}/build_container/hash" ]] || [[ "$(cat "${script_dir}/build_container/hash")" != "${chroot_hash}" ]]; then
        echo "Chroot file has changed, updating..."
        echo "${chroot_hash}" > "${script_dir}/build_container/hash"
        sudo docker import "${chroot_file}" "mcr.microsoft.com/cbl-mariner/containerized-rpmbuild:${version}"
    else
        echo "Chroot is up-to-date"
    fi
    container_img="mcr.microsoft.com/cbl-mariner/containerized-rpmbuild:${version}"
else
    container_img="mcr.microsoft.com/cbl-mariner/base/core:${version}"
fi

# ================== Launch Container ==================
echo "Checking if build env is up-to-date..."
docker_image_tag="mcr.microsoft.com/cbl-mariner/${USER}-containerized-rpmbuild:${version}"
sudo docker build -q \
                -f "${dockerfile}" \
                -t "${docker_image_tag}" \
                --build-arg container_img="$container_img" \
                --build-arg version="$version" \
                --build-arg enable_local_repo="$enable_local_repo" \
                --build-arg topdir="$topdir" \
                --build-arg mariner_repo="$repo_path" \
                --build-arg mariner_branch="$repo_branch" \
                --build-arg splash_txt="$splash_txt" \
                .

echo "docker_image_tag is ${docker_image_tag}"

sudo bash -c "docker run --rm \
                    ${mount_arg} \
                    -it ${docker_image_tag} /bin/bash; \
                    [[ -d ${repo_path}/out/RPMS/repodata ]] && { rm -r ${repo_path}/out/RPMS/repodata; echo 'Clearing repodata' ; }"
