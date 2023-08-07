// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

// Conversion to OVA format requires external tools:
// - sed (for inserting vmdk path into the VMX template)
// - ovftool (for expanding VMX template)
// - qemu-img (for converting RAW image to VMDK)
// - openssl (for generating manifest with sha1 file signatures)

package formats

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/file"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/logger"
	"github.com/microsoft/CBL-Mariner/toolkit/tools/internal/shell"

	"golang.org/x/sys/unix"
)

// OvaType represents the ova format
const (
	VmxTemplateVarName = "VMXTEMPLATE"
	OvfVarName         = "OVFINFO"
	OvaType            = "ova"
)

// Ova implements Converter interface to convert a RAW image into an OVA file
type Ova struct {
}

func filePathFromEnv(variable string) (path string, err error) {
	path, varExist := unix.Getenv(variable)
	if !varExist {
		err = fmt.Errorf("environment variable not found: %s", variable)
		return
	}

	fileExist, _ := file.PathExists(path)
	if !fileExist {
		err = fmt.Errorf("file from environment variable %s not found: %s", variable, path)
		return
	}
	return
}

// writeLines writes contents to file at path, appending newline characters to each line
// If createFile is true always creates a new file to write to
// If createFile is false append to the file if it exists
func writeLines(path string, contents []string, createFile bool) (err error) {
	var file *os.File
	if createFile {
		file, err = os.Create(path)
	} else {
		file, err = os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	}
	if err != nil {
		return
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	defer writer.Flush()

	for _, line := range contents {
		_, err = writer.WriteString(line + "\n")
		if err != nil {
			return
		}
	}

	return
}

// Convert converts the image in the OVA format
func (o *Ova) Convert(input, output string, isInputFile bool) (err error) {
	outputWithoutExtension := strings.TrimSuffix(output, filepath.Ext(output))
	logger.Log.Debugf("OVA filename without extension: %s", outputWithoutExtension)
	vmdkFilePath := outputWithoutExtension + ".vmdk"
	vmxFilePath := outputWithoutExtension + ".vmx"
	ovfFilePath := outputWithoutExtension + ".ovf"
	mfFilePath := outputWithoutExtension + ".mf"

	vmxTemplateFilePath, err := filePathFromEnv(VmxTemplateVarName)
	if err != nil {
		return
	}

	ovfInfoFilePath, err := filePathFromEnv(OvfVarName)
	if err != nil {
		return
	}

	// Insert disk path into the VMX template
	err = file.Copy(vmxTemplateFilePath, vmxFilePath)
	if err != nil {
		return
	}

	// Replace custom text with an disk image path
	err = shell.ExecuteLive(true, "sed", "-i", fmt.Sprintf("s|VMDK_IMAGE|%s|", vmdkFilePath), vmxFilePath)
	if err != nil {
		return
	}

	logger.Log.Infof(`Converting "%s" to "%s"`, input, vmdkFilePath)

	err = shell.ExecuteLiveWithCallback(logger.Log.Info, logger.Log.Warn, false, "qemu-img", "convert", "-f", "raw", input, "-O", "vmdk", vmdkFilePath)
	if err != nil {
		return err
	}

	// This step produces the disk1 vmdk and .mf files generated by ovftool from vmx template
	logger.Log.Debugf(`Expanding template "%s" to "%s"`, vmxFilePath, ovfFilePath)
	err = shell.ExecuteLiveWithCallback(logger.Log.Info, logger.Log.Warn, false, "ovftool", vmxFilePath, ovfFilePath)
	if err != nil {
		return
	}

	// Append product info to .ovf file
	if exist, _ := file.PathExists(ovfInfoFilePath); exist {
		var ovfLines, ovfInfoLines []string
		ovfInfoLines, err = file.ReadLines(ovfInfoFilePath)
		if err != nil {
			return
		}

		ovfLines, err = file.ReadLines(ovfFilePath)
		newLines := make([]string, 0, len(ovfInfoLines)+len(ovfLines))
		for _, ovfLine := range ovfLines {
			ovfLine := strings.TrimSpace(ovfLine)
			if ovfLine == "</VirtualHardwareSection>" {
				//ovfinfo file must contain the section end token
				newLines = append(newLines, ovfInfoLines...)
			} else {
				newLines = append(newLines, ovfLine)
			}
		}
		err = writeLines(ovfFilePath, newLines, true)
		if err != nil {
			return
		}

	}

	// Replace manifest file with updated signatures
	if exist, _ := file.PathExists(mfFilePath); exist {
		os.Remove(mfFilePath)
	}

	vmdkBase := filepath.Base(vmdkFilePath)
	vmdkDisk1FileName := strings.TrimSuffix(vmdkBase, filepath.Ext(vmdkBase)) + "-disk1.vmdk"
	vmdkDisk1FilePath := filepath.Join(filepath.Dir(vmdkFilePath), vmdkDisk1FileName)

	err = shell.ExecuteLiveWithCallback(logger.Log.Info, logger.Log.Warn, false, "openssl", "sha1", "-out", mfFilePath, vmdkDisk1FilePath, ovfFilePath)
	if err != nil {
		return
	}

	// Assume that all the files lie in the same directory (true since we copied/generated them)
	// To tar them at the toplevel folder
	ovfFileBase := filepath.Base(ovfFilePath)
	mfFileBase := filepath.Base(mfFilePath)
	vmdkDisk1FileBase := filepath.Base(vmdkDisk1FilePath)
	artifactsFolder, _ := filepath.Split(vmdkDisk1FilePath)

	// cd into the common directory to tar files at the toplevel directory
	logger.Log.Debugf("Changing directory to %s to run tar for OVA generation.", artifactsFolder)
	currentPwd, err := os.Getwd()
	if err != nil {
		return
	}
	os.Chdir(artifactsFolder)

	// OVA is just a tar archive with .ovf, .mf and other artifacts (disk)
	err = shell.ExecuteLiveWithCallback(logger.Log.Info, logger.Log.Warn, false, "tar", "-cf", output, "--format=ustar", ovfFileBase, mfFileBase, vmdkDisk1FileBase)

	logger.Log.Debugf("Changing directory back to %s after running tar for OVA generation.", currentPwd)
	os.Chdir(currentPwd)

	// Check error from creating OVA after going back to the old WD
	if err != nil {
		return
	}

	for _, path := range []string{vmdkFilePath, vmxFilePath, ovfFilePath, mfFilePath} {
		logger.Log.Debugf("Removing intermediate artifact %s", path)
		err = os.Remove(path)
		if err != nil {
			return
		}
	}

	logger.Log.Infof(`Created OVA file "%s"`, output)
	return
}

// Extension returns the filetype extension produced by this converter.
func (o *Ova) Extension() string {
	return OvaType
}

// NewOva returns a new .OVA format encoder
func NewOva() *Ova {
	return &Ova{}
}
