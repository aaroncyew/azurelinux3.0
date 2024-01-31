#!/bin/sh

# Description: This script is designed to mount a DM-Verity root filesystem and
# set up an OverlayFS. It is driven by kernel parameters and is invoked during
# the dracut initramfs phase.

# Kernel Parameters:
# - root: Specifies the path to the root filesystem. This script is designed to
#   support both DM-Verity protected devices and general filesystems. When a
#   DM-Verity protected device is detected (typically '/dev/mapper/root' for
#   systemd), the script performs steps specific to Verity. For non-DM-Verity
#   setups, the script will proceed with the standard OverlayFS setup, ensuring
#   versatility in its application.
# - rd.overlayfs: A comma-separated list defining the OverlayFS configuration.
#   Each entry should specify the overlay, upper, and work directories for an
#   OverlayFS instance.
# - rd.overlayfs_persistent_volume: Specifies the path to a persistent storage
#   volume to be used by OverlayFS. If not provided, a volatile (tmpfs) overlay
#   is created.

# Behavior:
# - Verifies the presence of the 'dracut-lib' for necessary utilities.
# - Mounts the DM-Verity root filesystem as read-only at a predefined mount
#   point.
# - Sets up the OverlayFS based on the provided kernel parameters. If a
#   persistent volume is specified, it's used as the upper layer for the
#   OverlayFS; otherwise, a volatile overlay is created.
# - Mounts the OverlayFS on top of the root filesystem, merging the read-only
#   root with the writable overlay, allowing system modifications without
#   altering the base system.

set -ex

parse_cmdline_args() {
    # Ensure that the 'dracut-lib' is present and loaded.
    type getarg >/dev/null 2>&1 || . /lib/dracut-lib.sh

    VERITY_MOUNT="/mnt/verity_mnt_$$"
    OVERLAY_MOUNT="/mnt/overlay_mnt_$$"
    OVERLAY_MNT_OPTS="rw,nodev,nosuid,nouser,noexec"

    # Retrieve the verity root. It is expected to be predefined by the dracut cmdline module.
    [ -z "$root" ] && root=$(getarg root=)
    # Check if we're in a dm-verity environment and the root variable matches
    # the expected path. The path "/dev/mapper/root" is hardcoded here because
    # it is a fixed target name generated by systemd-veritysetup. The name of
    # this dm-verity target is determined by systemd and cannot be changed,
    # hence the explicit check against this specific path.
    if [[ "$root" == *"/dev/mapper/root"* ]]; then
        is_verity=true
    else
        is_verity=false
    fi

    # Retrieve the OverlayFS parameters.
    [ -z "${overlayfs}" ] && overlayfs=$(getarg rd.overlayfs=)
    # Retrieve the persistent volume for the OverlayFS.
    [ -z "${overlayfs_persistent_volume}" ] && overlayfs_persistent_volume=$(getarg rd.overlayfs_persistent_volume=)
}

# Modified function to mount the physical partition
mount_physical_partition() {
    mkdir -p "${OVERLAY_MOUNT}"
    # Leverage the partition from cmdline
    local partition="${overlayfs_persistent_volume}"

    if [ -z "${partition}" ]; then
        # Fallback to volatile overlay if no persistent volume is specified
        echo "No overlayfs persistent volume specified. Creating a volatile overlay."
        mount -t tmpfs tmpfs -o ${OVERLAY_MNT_OPTS} "${OVERLAY_MOUNT}" || \
            die "Failed to create overlay tmpfs at ${OVERLAY_MOUNT}"
    else
        # Check if /etc/mdadm.conf exists.
        if [ -f "/etc/mdadm.conf" ]; then
            mdadm --assemble ${partition} || \
                die "Failed to assemble RAID volume."
        fi

        # Mount the specified persistent volume
        mount "${partition}" "${OVERLAY_MOUNT}" || \
            die "Failed to mount ${partition} at ${OVERLAY_MOUNT}"
    fi
}

create_overlay() {
    local _dir=$1
    local _mounted_dir="${VERITY_MOUNT}/${_dir}"
    local _upper=$2
    local _work=$3

    [ -d "$_mounted_dir" ] || die "Unable to create overlay as $_dir does not exist"

    mkdir -p "${_upper}" && \
    mkdir -p "${_work}" && \
    mount -t overlay overlay -o ro,lowerdir="${_mounted_dir}",upperdir="${_upper}",workdir="${_work}" "${_mounted_dir}" || \
        die "Failed to mount overlay in ${_mounted_dir}"
}

mount_root() {
    if [ "$is_verity" = true ]; then
        echo "Mounting DM-Verity Target"
        mkdir -p "${VERITY_MOUNT}"
        mount -o ro,defaults "/dev/mapper/root" "${VERITY_MOUNT}" || \
            die "Failed to mount dm-verity root target"
    else
        echo "Mounting regular root"
        mkdir -p "${VERITY_MOUNT}"
        mount -o ro,defaults "$root" "${VERITY_MOUNT}" || \
            die "Failed to mount root"
    fi

    mount_physical_partition

    echo "Starting to create OverlayFS"
    for _group in ${overlayfs}; do
        IFS=',' read -r overlay upper work <<< "$_group"
        echo "Creating OverlayFS with overlay: $overlay, upper: ${OVERLAY_MOUNT}/${upper}, work: ${OVERLAY_MOUNT}/${work}"
        create_overlay "$overlay" "${OVERLAY_MOUNT}/${upper}" "${OVERLAY_MOUNT}/${work}"
    done

    echo "Done Verity Root Mounting and OverlayFS Mounting"
    # Re-mount the verity mount along with overlayfs to the sysroot.
    mount --rbind "${VERITY_MOUNT}" "${NEWROOT}"
}

parse_cmdline_args
mount_root
