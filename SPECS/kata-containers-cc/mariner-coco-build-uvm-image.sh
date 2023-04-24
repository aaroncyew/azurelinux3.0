#!/bin/bash
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

set -e
set -o errexit

[ -n "${DEBUG:-}" ] && set -o xtrace

readonly SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
readonly IMAGE_BUILD_ROOT=`mktemp --directory -t mariner-coco-build-uvm-image-XXXXXX`

generate_image()
{
    mv ${ROOT_FOLDER}/nsdax.gpl.c "${IMAGE_BUILD_ROOT}"
    sudo cp -r ${ROOT_FOLDER}/opt ${IMAGE_BUILD_ROOT}
    cd "${IMAGE_BUILD_ROOT}"

    # move rootfs
    sudo mv $ROOT_FOLDER/rootfs-cbl-mariner ${IMAGE_BUILD_ROOT}/rootfs-cbl-mariner

    gcc -O2 ./nsdax.gpl.c -o ${IMAGE_BUILD_ROOT}/nsdax

    # build image
    sudo DEBUG=1 \
      NSDAX_BIN=${IMAGE_BUILD_ROOT}/nsdax \
      ${IMAGE_BUILD_ROOT}/opt/mariner/share/uvm/tools/osbuilder/image-builder/image_builder.sh ${IMAGE_BUILD_ROOT}/rootfs-cbl-mariner

    sudo cp kata-containers.img $OUT_DIR

    sudo rm -rf "${IMAGE_BUILD_ROOT}"
}


while getopts ":r:p:o:" OPTIONS; do
  case "${OPTIONS}" in
    r ) ROOT_FOLDER=$OPTARG ;;
    p ) RPM_DIR=$OPTARG ;;
    o ) OUT_DIR=$OPTARG ;;

    \? )
        echo "Error - Invalid Option: -$OPTARG" 1>&2
        exit 1
        ;;
    : )
        echo "Error - Invalid Option: -$OPTARG requires an argument" 1>&2
        exit 1
        ;;
  esac
done

echo "-- ROOT_FOLDER -> $ROOT_FOLDER"
echo "-- RPM_DIR -> $RPM_DIR"
echo "-- OUT_DIR -> $OUT_DIR"

generate_image $*
