// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

// A tool for generating snapshots of built RPMs from local specs.

package rpmssnapshot

import (
	"fmt"
	"path/filepath"
	"regexp"
	"runtime"

	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/file"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/jsonutils"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/logger"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/packagerepo/repocloner"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/rpm"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/pkg/simplechroottool"
)

const (
	chrootOutputFilePath = "/snapshot.json"
)

// Regular expression to extract package name, version, distribution, and architecture from values returned by 'rpmspec --builtrpms'.
// Examples:
//
//	kernel-5.15.63.1-1.cm2.x86_64		->	Name: kernel, Version: 5.15.63.1-1, Distribution: cm2, Architecture: x86_64
//	python3-perf-5.15.63.1-1.cm2.x86_64	->	Name: python3-perf, Version: 5.15.63.1-1, Distribution: cm2, Architecture: x86_64
//
// NOTE: regular expression based on following assumptions:
//   - Package version and release values are not allowed to contain a hyphen character.
//   - Our tooling prevents the 'Release' tag from having any other form than '[[:digit:]]+%{?dist}'
//   - The distribution tag is not allowed to contain a period or a hyphen.
//   - The architecture is not allowed to contain a period or a hyphen.
//
// Regex breakdown:
//
//	^(.*)			<-- [index 1] package name
//	-				<-- second-to-last hyphen separating the package name from its version
//	([^-]+-\d+)		<-- [index 2] package version and package release number connected by the last hyphen
//	\.				<-- second-to-last period separating the package release number from the distribution tag
//	([^.]+)			<-- [index 3] the distribution tag
//	\.				<-- last period separating the distribution tag from the architecture string
//	([^.]+)$		<-- [index 4] the architecture string
var rpmSpecBuiltRPMRegex = regexp.MustCompile(`^(.*)-([^-]+-\d+)\.([^.]+)\.([^.]+)$`)

const (
	rpmSpecBuiltRPMRegexNameIndex = iota + 1
	rpmSpecBuiltRPMRegexVersionIndex
	rpmSpecBuiltRPMRegexDistributionIndex
	rpmSpecBuiltRPMRegexArchitectureIndex
	rpmSpecBuiltRPMRegexMatchesCount

	chrootName = "rpmssnapshot_chroot"
	runChecks  = false
)

type SnapshotGenerator struct {
	simplechroottool.SimpleChrootTool
}

// New creates a new snapshot generator.
func New(buildDirPath, workerTarPath, specsDirPath, distTag string) (newSnapshotGenerator *SnapshotGenerator, err error) {
	newSnapshotGenerator = &SnapshotGenerator{}
	err = newSnapshotGenerator.InitializeChroot(buildDirPath, chrootName, workerTarPath, specsDirPath, distTag, runChecks)

	return newSnapshotGenerator, err
}

// GenerateSnapshot generates a snapshot of all packages built from the specs inside the input directory.
func (s *SnapshotGenerator) GenerateSnapshot(outputFilePath string) (err error) {
	err = s.RunInChroot(func() error {
		return s.generateSnapshotInChroot()
	})
	if err != nil {
		return
	}

	chrootOutputFileFullPath := filepath.Join(s.ChrootRootDir(), chrootOutputFilePath)
	err = file.Move(chrootOutputFileFullPath, outputFilePath)
	if err != nil {
		logger.Log.Errorf("Failed to retrieve the snapshot from the chroot. Error: %v.", err)
	}

	return
}

func (s *SnapshotGenerator) convertResultsToRepoContents(allBuiltRPMs []string) (repoContents repocloner.RepoContents, err error) {
	repoContents = repocloner.RepoContents{
		Repo: []*repocloner.RepoPackage{},
	}

	for _, builtRPM := range allBuiltRPMs {
		matches := rpmSpecBuiltRPMRegex.FindStringSubmatch(builtRPM)
		if len(matches) != rpmSpecBuiltRPMRegexMatchesCount {
			return repoContents, fmt.Errorf("RPM package name (%s) doesn't match the regular expression (%s)", builtRPM, rpmSpecBuiltRPMRegex.String())
		}

		repoContents.Repo = append(repoContents.Repo, &repocloner.RepoPackage{
			Name:         matches[rpmSpecBuiltRPMRegexNameIndex],
			Version:      matches[rpmSpecBuiltRPMRegexVersionIndex],
			Distribution: matches[rpmSpecBuiltRPMRegexDistributionIndex],
			Architecture: matches[rpmSpecBuiltRPMRegexArchitectureIndex],
		})
	}

	return
}

func (s *SnapshotGenerator) generateSnapshotInChroot() (err error) {
	var (
		allBuiltRPMs []string
		repoContents repocloner.RepoContents
		specPaths    []string
	)

	defines := s.DefaultDefines()
	specPaths, err = rpm.BuildCompatibleSpecsList(s.ChrootRelativeSpecDir(), []string{}, defines)
	if err != nil {
		logger.Log.Errorf("Failed to retrieve a list of specs inside (%s). Error: %v.", s.ChrootRelativeSpecDir(), err)
		return
	}

	logger.Log.Infof("Found %d compatible specs.", len(specPaths))

	allBuiltRPMs, err = s.readBuiltRPMs(specPaths, defines)
	if err != nil {
		logger.Log.Errorf("Failed to extract built RPMs from specs. Error: %v.", err)
		return
	}

	logger.Log.Infof("The specs build %d packages in total.", len(allBuiltRPMs))

	repoContents, err = s.convertResultsToRepoContents(allBuiltRPMs)
	if err != nil {
		logger.Log.Errorf("Failed to convert RPMs list to a packages summary file. Error: %v.", err)
		return
	}

	err = jsonutils.WriteJSONFile(chrootOutputFilePath, repoContents)
	if err != nil {
		logger.Log.Errorf("Failed to save results into (%s). Error: %v.", chrootOutputFilePath, err)
	}

	return
}

func (s *SnapshotGenerator) readBuiltRPMs(specPaths []string, defines map[string]string) (allBuiltRPMs []string, err error) {
	var builtRPMs []string

	buildArch, err := rpm.GetRpmArch(runtime.GOARCH)
	if err != nil {
		return
	}

	for _, specPath := range specPaths {
		logger.Log.Debugf("Parsing spec (%s).", specPath)

		specDirPath := filepath.Dir(specPath)

		builtRPMs, err = rpm.QuerySPECForBuiltRPMs(specPath, specDirPath, buildArch, defines)
		if err != nil {
			logger.Log.Errorf("Failed to query built RPMs from (%s). Error: %v.", specPath, err)
			return
		}

		allBuiltRPMs = append(allBuiltRPMs, builtRPMs...)
	}

	return
}
