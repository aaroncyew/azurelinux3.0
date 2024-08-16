// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package imagecustomizerapi

import (
	"fmt"
	"path"
	"strings"
)

type Overlay struct {
	LowerDir          string   `yaml:"lowerDir"`
	UpperDir          string   `yaml:"upperDir"`
	WorkDir           string   `yaml:"workDir"`
	MountPoint        string   `yaml:"mountPoint"`
	IsRootfsOverlay   bool     `yaml:"isRootfsOverlay"`
	MountDependencies []string `yaml:"mountDependencies"`
	MountOptions      string   `yaml:"mountOptions"`
}

func (o *Overlay) IsValid() error {
	// Validate paths for UpperDir, WorkDir, and LowerDir
	if err := validatePath(o.LowerDir); err != nil {
		return fmt.Errorf("invalid lowerDir (%s):\n%w", o.LowerDir, err)
	}
	if err := validatePath(o.UpperDir); err != nil {
		return fmt.Errorf("invalid upperDir (%s):\n%w", o.UpperDir, err)
	}
	if err := validatePath(o.WorkDir); err != nil {
		return fmt.Errorf("invalid workDir (%s):\n%w", o.WorkDir, err)
	}
	if err := validatePath(o.MountPoint); err != nil {
		return fmt.Errorf("invalid mountPoint (%s):\n%w", o.MountPoint, err)
	}
	for _, dependency := range o.MountDependencies {
		if err := validatePath(dependency); err != nil {
			return fmt.Errorf("invalid mountDependencies (%s):\n%w", dependency, err)
		}
	}

	if strings.Contains(o.MountOptions, " ") {
		return fmt.Errorf("mountOptions (%s) contains spaces and is invalid", o.MountOptions)
	}

	// Check if UpperDir and WorkDir are identical
	if o.UpperDir == o.WorkDir {
		return fmt.Errorf("upperDir and workDir must be distinct, but both are '%s'", o.UpperDir)
	}

	// Check if UpperDir is a subdirectory of WorkDir or vice versa
	if isSubDirString(o.UpperDir, o.WorkDir) {
		return fmt.Errorf("upperDir (%s) should not be a subdirectory of workDir (%s)", o.UpperDir, o.WorkDir)
	}
	if isSubDirString(o.WorkDir, o.UpperDir) {
		return fmt.Errorf("workDir (%s) should not be a subdirectory of upperDir (%s)", o.WorkDir, o.UpperDir)
	}

	return nil
}

func validatePath(filePath string) error {
	// Check if the path is empty.
	if filePath == "" {
		return fmt.Errorf("path cannot be empty")
	}

	// Check if the path contains spaces.
	if strings.Contains(filePath, " ") {
		return fmt.Errorf("path (%s) contains spaces and is invalid", filePath)
	}

	// Check if the path is an absolute path.
	if !path.IsAbs(filePath) {
		return fmt.Errorf("invalid path (%s): must be an absolute path", filePath)
	}

	return nil
}

func isSubDirString(dir1, dir2 string) bool {
	// Ensure paths are cleaned and have consistent trailing slashes
	cleanDir1 := strings.TrimSuffix(dir1, "/") + "/"
	cleanDir2 := strings.TrimSuffix(dir2, "/") + "/"

	// Check if dir2 starts with dir1 (indicating a subdirectory)
	return cleanDir1 != cleanDir2 && strings.HasPrefix(cleanDir2, cleanDir1)
}
