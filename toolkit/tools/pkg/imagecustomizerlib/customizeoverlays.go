// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package imagecustomizerlib

import (
	"fmt"
	"os"
	"path"
	"path/filepath"
	"strings"

	"github.com/microsoft/azurelinux/toolkit/tools/imagecustomizerapi"
	"github.com/microsoft/azurelinux/toolkit/tools/imagegen/diskutils"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/logger"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/safechroot"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/shell"
)

func enableOverlays(overlays *[]imagecustomizerapi.Overlay, selinuxMode imagecustomizerapi.SELinuxMode,
	imageChroot *safechroot.Chroot,
) (bool, error) {
	var err error

	if overlays == nil {
		return false, nil
	}

	logger.Log.Infof("Enable filesystem overlays")

	// Integrate overlay driver into the initramfs img.
	overlayDriver := "overlay"
	err = addDracutDriver(overlayDriver, imageChroot)
	if err != nil {
		return false, err
	}

	// Dereference the pointer to get the slice
	overlaysDereference := *overlays
	err = updateFstabForOverlays(overlaysDereference, imageChroot)
	if err != nil {
		return false, fmt.Errorf("failed to update fstab file for overlays:\n%w", err)
	}

	// Create necessary directories for overlays
	err = createOverlayDirectories(overlaysDereference, imageChroot)
	if err != nil {
		return false, fmt.Errorf("failed to create overlay directories:\n%w", err)
	}

	// Add equivalency rules for each overlay
	err = addEquivalencyRules(selinuxMode, overlaysDereference, imageChroot)
	if err != nil {
		return false, fmt.Errorf("failed to add equivalency rules for overlays:\n%w", err)
	}

	return true, nil
}

func updateFstabForOverlays(overlays []imagecustomizerapi.Overlay, imageChroot *safechroot.Chroot,
) error {
	var err error

	fstabFile := filepath.Join(imageChroot.RootDir(), "etc/fstab")
	fstabEntries, err := diskutils.ReadFstabFile(fstabFile)
	if err != nil {
		return fmt.Errorf("failed to read fstab file: %v", err)
	}

	var updatedEntries []diskutils.FstabEntry
	updatedEntries = append(updatedEntries, fstabEntries...)

	for _, overlay := range overlays {
		lowerDirs := overlay.LowerDirs
		upperDir := overlay.UpperDir
		workDir := overlay.WorkDir
		mountDependencies := overlay.MountDependencies

		// Validate that each mountDependency has the x-initrd.mount option in
		// the corresponding fstab entry.
		for _, dep := range mountDependencies {
			found := false
			for _, entry := range fstabEntries {
				if entry.Target == dep {
					found = true
					// Split the options by comma and check if x-initrd.mount is present
					options := strings.Split(entry.Options, ",")
					optionFound := false
					for _, option := range options {
						if option == "x-initrd.mount" {
							optionFound = true
							break
						}
					}
					if !optionFound {
						return fmt.Errorf("mountDependency %s requires x-initrd.mount option in fstab", dep)
					}
					break
				}
			}
			if !found {
				return fmt.Errorf("mountDependency %s not found in fstab", dep)
			}
		}

		if overlay.IsRootfsOverlay {
			for i, dir := range lowerDirs {
				lowerDirs[i] = path.Join("/sysroot", dir)
			}
			upperDir = path.Join("/sysroot", overlay.UpperDir)
			workDir = path.Join("/sysroot", overlay.WorkDir)
			for i, dep := range mountDependencies {
				mountDependencies[i] = path.Join("/sysroot", dep)
			}
		}

		// Multiple lower layers can be specified by joining directory names
		// with a colon (":") as a separator, which is supported by the overlay
		// filesystem in the mount command.
		lowerDirOption := strings.Join(lowerDirs, ":")

		options := fmt.Sprintf("lowerdir=%s,upperdir=%s,workdir=%s", lowerDirOption, upperDir, workDir)

		// Add any additional options if needed (e.g., x-initrd.mount,
		// x-systemd.requires)
		for _, dep := range mountDependencies {
			options = fmt.Sprintf("%s,x-systemd.requires=%s", options, dep)
		}
		if overlay.IsRootfsOverlay {
			options = fmt.Sprintf("%s,x-initrd.mount", options)
		}
		if overlay.MountOptions != "" {
			options = fmt.Sprintf("%s,%s", options, overlay.MountOptions)
		}

		// Create the FstabEntry based on the overlay.
		newEntry := diskutils.FstabEntry{
			Source:  "overlay",
			Target:  overlay.MountPoint,
			FsType:  "overlay",
			Options: options,
			Freq:    0,
			PassNo:  0,
		}

		updatedEntries = append(updatedEntries, newEntry)
	}

	err = diskutils.WriteFstabFile(updatedEntries, fstabFile)
	if err != nil {
		return err
	}

	return nil
}

func createOverlayDirectories(overlays []imagecustomizerapi.Overlay, imageChroot *safechroot.Chroot) error {
	for _, overlay := range overlays {
		dirsToCreate := []string{
			filepath.Join(imageChroot.RootDir(), overlay.MountPoint),
			filepath.Join(imageChroot.RootDir(), overlay.UpperDir),
			filepath.Join(imageChroot.RootDir(), overlay.WorkDir),
		}

		// Iterate over each directory and create it if it doesn't exist.
		for _, dir := range dirsToCreate {
			if err := os.MkdirAll(dir, os.ModePerm); err != nil {
				return fmt.Errorf("failed to create directory (%s): %w", dir, err)
			}
		}
	}

	return nil
}

func addEquivalencyRules(selinuxMode imagecustomizerapi.SELinuxMode,
	overlays []imagecustomizerapi.Overlay, imageChroot *safechroot.Chroot,
) error {
	var err error

	if selinuxMode == imagecustomizerapi.SELinuxModeDisabled {
		// No need to add equivalency rules if SELinux is disabled.
		return nil
	}

	for _, overlay := range overlays {
		err = imageChroot.UnsafeRun(func() error {
			return shell.ExecuteLiveWithErr(1, "sudo", "semanage", "fcontext", "-a", "-e", overlay.MountPoint, overlay.UpperDir)
		})
		if err != nil {
			return fmt.Errorf("failed to add equivalency rule between %s and %s:\n%w", overlay.MountPoint, overlay.UpperDir, err)
		}
	}

	return nil
}
