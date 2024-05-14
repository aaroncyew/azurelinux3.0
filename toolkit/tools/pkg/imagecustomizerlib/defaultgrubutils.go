// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package imagecustomizerlib

import (
	"fmt"
	"path/filepath"
	"strings"

	"github.com/microsoft/azurelinux/toolkit/tools/imagegen/installutils"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/file"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/grub"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/logger"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/safechroot"
)

const (
	// A string that is present in the /boot/grub2/grub.cfg when it is generated by grub-mkconfig.
	grubMkconfigHeader = "automatically generated by grub2-mkconfig"

	defaultGrubCmdlineLinux        = "GRUB_CMDLINE_LINUX"
	defaultGrubCmdlineLinuxDefault = "GRUB_CMDLINE_LINUX_DEFAULT"
	grubKernelOpts                 = "kernelopts"

	// The variable in the /etc/default/grub file that contains the SELinux args.
	defaultGrubVarCmdlineForSELinux = defaultGrubCmdlineLinux
)

type grubDefaultVarAssign struct {
	Token grub.Token
	Name  string
	Value string
}

// Takes the string contents of a /etc/default/grub file and looks for all the variable assignment statements.
func findGrubDefaultVarAssigns(grubDefaultConfig string) ([]grubDefaultVarAssign, error) {
	// So, technically the /etc/default/grub file is a Bash file not a grub config file.
	// While these are very similar formats, they do have differences.
	// But, we are just going to hope that the user isn't annoying enough to Bash specifc features within
	// /etc/default/grub file. (e.g. <<< strings.)
	grubTokens, err := grub.TokenizeConfig(grubDefaultConfig)
	if err != nil {
		return nil, err
	}

	varAssigns := []grubDefaultVarAssign(nil)

	lines := grub.SplitTokensIntoLines(grubTokens)
	for _, line := range lines {
		if len(line) != 1 {
			// Normal variable assignments only have 1 value.
			// Export variable assignments have 2 values. But we are ignoring those.
			continue
		}

		argToken := line[0]

		isVarAssign := len(argToken.SubWords) >= 1 &&
			argToken.SubWords[0].Type == grub.KEYWORD_STRING &&
			strings.Contains(argToken.SubWords[0].Value, "=")

		if !isVarAssign {
			continue
		}

		argStringBuilder := strings.Builder{}
		for _, subword := range argToken.SubWords {
			switch subword.Type {
			case grub.KEYWORD_STRING, grub.STRING:
				argStringBuilder.WriteString(subword.Value)

			case grub.QUOTED_VAR_EXPANSION:
				if subword.Value != grubKernelOpts {
					return nil, fmt.Errorf("unexpected quoted variable expansion (%s)", subword.Value)
				}

				// There is a bug in Azure Linux 2.0 and early builds of Azure Linux 3.0 where "$kernelopts" is not
				// properly escaped.
				// So, be nice and fix it up.
				argStringBuilder.WriteString("$")
				argStringBuilder.WriteString(grubKernelOpts)

			case grub.VAR_EXPANSION:
				return nil, fmt.Errorf("unexpected variable expansion (%s)", subword.Value)
			}
		}

		argValue := argStringBuilder.String()
		name, value, foundEqSymbol := strings.Cut(argValue, "=")
		if !foundEqSymbol {
			// Not a variable assignment.
			continue
		}

		varAssign := grubDefaultVarAssign{
			Token: argToken,
			Name:  name,
			Value: value,
		}
		varAssigns = append(varAssigns, varAssign)
	}

	return varAssigns, nil
}

// Takes the list of variable assignments in a /etc/defaukt/grub file and looks for the assignment to the variables that
// matches the provided name.
func findGrubDefaultVarAssign(varAssigns []grubDefaultVarAssign, name string) (grubDefaultVarAssign, error) {
	for _, varAssign := range varAssigns {
		if varAssign.Name == name {
			return varAssign, nil
		}
	}

	err := fmt.Errorf("failed to find %s variable assignment (%s)", installutils.GrubDefFile, name)
	return grubDefaultVarAssign{}, err
}

// Takes the string contents of a /etc/default/grub file and the name of the command-line args variable (either
// "GRUB_CMDLINE_LINUX" or "GRUB_CMDLINE_LINUX_DEFAULT") and returns a list of kernel command-line args.
//
// Params:
//   - defaultGrubContent: The string contents of the /etc/default/grub file.
//   - varName: The name of variable that contains kernel command-line args. Either "GRUB_CMDLINE_LINUX" or
//     "GRUB_CMDLINE_LINUX_DEFAULT".
//
// Returns:
//   - cmdLineVarAssign: The variable assignment that matches 'varName'.
//   - args: The list of kernel command-line args.
//   - insertAt: An index that new kernel command-line args can be inserted at.
func getGrubDefaultLinuxArgs(defaultGrubContent string, varName string,
) (grubDefaultVarAssign, []grubConfigLinuxArg, int, error) {
	varAssigns, err := findGrubDefaultVarAssigns(defaultGrubContent)
	if err != nil {
		err = fmt.Errorf("failed to parse %s file:\n%w", installutils.GrubDefFile, err)
		return grubDefaultVarAssign{}, nil, 0, err
	}

	// Find the variable's (e.g. GRUB_CMDLINE_LINUX) line.
	cmdLineVarAssign, err := findGrubDefaultVarAssign(varAssigns, varName)
	if err != nil {
		return grubDefaultVarAssign{}, nil, 0, err
	}

	// The (parsed) string value of the variable is copied verbatim into the grub.cfg file.
	// So, args can have quotes if needed, but those quotes will be double escaped.
	argsString := cmdLineVarAssign.Value
	grubTokens, err := grub.TokenizeConfig(argsString)
	if err != nil {
		err = fmt.Errorf("failed to parse %s's value:\n%w", varName, err)
		return grubDefaultVarAssign{}, nil, 0, err
	}

	var insertAt int
	if varName == defaultGrubCmdlineLinuxDefault {
		// GRUB_CMDLINE_LINUX_DEFAULT variable has the $kernelopts arg.
		// Any args inserted should be inserted before $kernelopts.
		insertAt, err = findCommandLineInsertAt(grubTokens)
		if err != nil {
			err = fmt.Errorf("failed to parse %s's value args:\n%w", varName, err)
			return grubDefaultVarAssign{}, nil, 0, err
		}
	} else {
		// Insert args at the end of the string.
		insertAt = len(argsString)
	}

	args, err := parseCommandLineArgs(grubTokens)
	if err != nil {
		err = fmt.Errorf("failed to parse %s's value args:\n%w", varName, err)
		return grubDefaultVarAssign{}, nil, 0, err
	}

	return cmdLineVarAssign, args, insertAt, nil
}

// Takes the string contents of /etc/default/grub file and inserts the provided command-line args.
func addExtraCommandLineToDefaultGrubFile(defaultGrubContent string, extraCommandLine string) (string, error) {
	cmdLineVarAssign, _, insertAt, err := getGrubDefaultLinuxArgs(defaultGrubContent,
		defaultGrubCmdlineLinuxDefault)
	if err != nil {
		return "", err
	}

	argsString := cmdLineVarAssign.Value

	// Add the extra command-line args.
	argsString = argsString[:insertAt] + " " + extraCommandLine + " " + argsString[insertAt:]

	// Rewrite GRUB_CMDLINE_LINUX_DEFAULT line.
	defaultGrubContent = rewriteDefaultGrubLine(defaultGrubContent, cmdLineVarAssign, argsString)
	return defaultGrubContent, nil
}

// Takes the string contents of the /etc/default/grub file and replaces a set of command-line args.
//
// Params:
//   - defaultGrubContent: The string contents of the /etc/default/grub file.
//   - varName: The name of the variable assignment to modify. Either "GRUB_CMDLINE_LINUX" or
//     "GRUB_CMDLINE_LINUX_DEFAULT".
//   - argsToRemove: A list of arg names to remove from the kernel command-line.
//   - newArgs: A list of new arg values to add to the kernel command-line.
//
// Returns:
//   - defaultGrubContent: The new string contents of the /etc/default/grub file.
func updateDefaultGrubKernelCommandLineArgs(defaultGrubContent string, varName string, argsToRemove []string,
	newArgs []string,
) (string, error) {
	cmdLineVarAssign, args, insertAt, err := getGrubDefaultLinuxArgs(defaultGrubContent, varName)
	if err != nil {
		return "", err
	}

	value := cmdLineVarAssign.Value
	value, err = updateKernelCommandLineArgsHelper(value, args, insertAt, argsToRemove, newArgs)
	if err != nil {
		return "", err
	}

	// Rewrite GRUB_CMDLINE_LINUX line.
	defaultGrubContent = rewriteDefaultGrubLine(defaultGrubContent, cmdLineVarAssign, value)
	return defaultGrubContent, nil
}

// Takes the string contents of the /etc/default/grub file and rewrites one of the variable assignments lines.
//
// Params:
//   - defaultGrubContent: The string contents of the /etc/default/grub file.
//   - varAssign: The variable assignment statement to replace.
//   - newValue: The string value to assign to the variable.
func rewriteDefaultGrubLine(defaultGrubContent string, varAssign grubDefaultVarAssign, newValue string) string {
	// Rewrite the GRUB_CMDLINE_LINUX_DEFAULT line.
	cmdLineString := fmt.Sprintf("%s=%s", varAssign.Name, grub.ForceQuoteString(newValue))

	start := varAssign.Token.Loc.Start.Index
	end := varAssign.Token.Loc.End.Index

	// Rewrite the /etc/default/grub file.
	defaultGrubContent = defaultGrubContent[:start] + cmdLineString + defaultGrubContent[end:]
	return defaultGrubContent
}

// Checks if the image uses grub-mkconfig.
func isGrubMkconfigEnabled(imageChroot *safechroot.Chroot) (bool, error) {
	grub2ConfigFile, err := readGrub2ConfigFile(imageChroot)
	if err != nil {
		return false, err
	}

	grubMkconfigEnabled := isGrubMkconfigConfig(grub2ConfigFile)
	return grubMkconfigEnabled, nil
}

// Takes the string contents of the grub.cfg file and checks if it was generated by the grub-mkconfig tool.
func isGrubMkconfigConfig(grub2Config string) bool {
	grubMkconfigEnabled := strings.Contains(grub2Config, grubMkconfigHeader)
	return grubMkconfigEnabled
}

// Reads the string contents of the /etc/default/grub file.
func readDefaultGrubFile(imageChroot *safechroot.Chroot) (string, error) {
	logger.Log.Debugf("Reading %s file", installutils.GrubDefFile)

	grub2ConfigFilePath := getGrubDefaultFilePath(imageChroot)

	// Read the existing grub.cfg file.
	grub2Config, err := file.Read(grub2ConfigFilePath)
	if err != nil {
		return "", fmt.Errorf("failed to read grub file (%s):\n%w", installutils.GrubDefFile, err)
	}

	return grub2Config, nil
}

// Writes the string contents of the /etc/default/grub file.
func writeDefaultGrubFile(grub2Config string, imageChroot *safechroot.Chroot) error {
	logger.Log.Debugf("Writing %s file", installutils.GrubDefFile)

	grub2ConfigFilePath := getGrubDefaultFilePath(imageChroot)

	// Update grub.cfg file.
	err := file.Write(grub2Config, grub2ConfigFilePath)
	if err != nil {
		return fmt.Errorf("failed to write grub file (%s):\n%w", installutils.GrubDefFile, err)
	}

	return nil
}

func getGrubDefaultFilePath(imageChroot *safechroot.Chroot) string {
	return filepath.Join(imageChroot.RootDir(), installutils.GrubDefFile)
}
