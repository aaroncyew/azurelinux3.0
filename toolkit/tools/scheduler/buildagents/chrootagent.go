// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package buildagents

import (
	"fmt"
	"path/filepath"
	"strings"

	"microsoft.com/pkggen/internal/logger"
	"microsoft.com/pkggen/internal/shell"
)

// ChrootAgentFlag is the build-agent option for ChrootAgent.
const ChrootAgentFlag = "chroot-agent"

// ChrootAgent implements the BuildAgent interface to build SRPMs using a local chroot.
type ChrootAgent struct {
	config *BuildAgentConfig
}

// NewChrootAgent returns a new ChrootAgent.
func NewChrootAgent() *ChrootAgent {
	return &ChrootAgent{}
}

// Initialize initializes the chroot agent with the given configuration.
func (c *ChrootAgent) Initialize(config *BuildAgentConfig) (err error) {
	c.config = config
	return
}

// BuildPackage builds a given file and returns the output files or error.
// - inputFile is the SRPM to build.
// - logFile is the file name to save the package build log to.
func (c *ChrootAgent) BuildPackage(inputFile, logName string) (builtFiles []string, logFile string, err error) {
	// On success, pkgworker will print a comma-seperated list of all RPMs built to stdout.
	// This will be the last stdout line written.
	const delimiter = ","

	logFile = filepath.Join(c.config.LogDir, logName)

	var lastStdoutLine string
	onStdout := func(args ...interface{}) {
		if len(args) == 0 {
			return
		}

		lastStdoutLine = strings.TrimSpace(args[0].(string))
		logger.Log.Trace(lastStdoutLine)
	}

	args := serializeChrootBuildAgentConfig(c.config, inputFile, logFile)
	err = shell.ExecuteLiveWithCallback(onStdout, logger.Log.Trace, c.config.Program, args...)

	if err == nil && lastStdoutLine != "" {
		builtFiles = strings.Split(lastStdoutLine, delimiter)
	}

	return
}

// Config returns a copy of the agent's configuration.
func (c *ChrootAgent) Config() (config BuildAgentConfig) {
	return *c.config
}

// Close closes the ChrootAgent, releasing any resources.
func (c *ChrootAgent) Close() (err error) {
	return
}

// serializeChrootBuildAgentConfig serializes a BuildAgentConfig into arguments usable by pkgworker.
func serializeChrootBuildAgentConfig(config *BuildAgentConfig, inputFile, logFile string) (serializedArgs []string) {
	serializedArgs = []string{
		fmt.Sprintf("--input=%s", inputFile),
		fmt.Sprintf("--work-dir=%s", config.WorkDir),
		fmt.Sprintf("--worker-tar=%s", config.WorkerTar),
		fmt.Sprintf("--repo-file=%s", config.RepoFile),
		fmt.Sprintf("--rpm-dir=%s", config.RpmDir),
		fmt.Sprintf("--srpm-dir=%s", config.SrpmDir),
		fmt.Sprintf("--cache-dir=%s", config.CacheDir),
		fmt.Sprintf("--dist-tag=%s", config.DistTag),
		fmt.Sprintf("--distro-release-version=%s", config.DistroReleaseVersion),
		fmt.Sprintf("--distro-build-number=%s", config.DistroBuildNumber),
		fmt.Sprintf("--log-file=%s", logFile),
		fmt.Sprintf("--log-level=%s", config.LogLevel),
	}

	if config.RpmmacrosFile != "" {
		serializedArgs = append(serializedArgs, fmt.Sprintf("--rpmmacros-file=%s", config.RpmmacrosFile))
	}

	if config.NoCleanup {
		serializedArgs = append(serializedArgs, "--no-cleanup")
	}

	if config.RunCheck {
		serializedArgs = append(serializedArgs, "--run-check")
	}

	return
}
