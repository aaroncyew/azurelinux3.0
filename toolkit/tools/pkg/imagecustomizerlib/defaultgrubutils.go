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

	grubKernelOpts = "kernelopts"
)

type defaultGrubFileVarName string

const (
	defaultGrubFileVarNameCmdlineLinux        defaultGrubFileVarName = "GRUB_CMDLINE_LINUX"
	defaultGrubFileVarNameCmdlineLinuxDefault defaultGrubFileVarName = "GRUB_CMDLINE_LINUX_DEFAULT"

	// The variable in the /etc/default/grub file that contains the SELinux args.
	defaultGrubFileVarNameCmdlineForSELinux = defaultGrubFileVarNameCmdlineLinux
)

type defaultGrubFileVarAssign struct {
	Token grub.Token
	Line  grub.Line
	Name  string
	Value string
}

// Takes the string contents of a /etc/default/grub file and looks for all the variable assignment statements.
func findDefaultGrubFileVarAssigns(defaultGrubFileContent string) ([]defaultGrubFileVarAssign, error) {
	// So, technically the /etc/default/grub file is a Bash file not a grub config file.
	// While these are very similar formats, they do have differences.
	// But, we are just going to hope that the user isn't annoying enough to Bash specifc features within
	// /etc/default/grub file. (e.g. <<< strings.)
	grubTokens, err := grub.TokenizeConfig(defaultGrubFileContent)
	if err != nil {
		return nil, err
	}

	varAssigns := []defaultGrubFileVarAssign(nil)

	lines := grub.SplitTokensIntoLines(grubTokens)
	for _, line := range lines {
		if len(line.Tokens) != 1 {
			// Normal variable assignments only have 1 value.
			// Export variable assignments have 2 values. But we are ignoring those.
			continue
		}

		argToken := line.Tokens[0]

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

		varAssign := defaultGrubFileVarAssign{
			Token: argToken,
			Line:  line,
			Name:  name,
			Value: value,
		}
		varAssigns = append(varAssigns, varAssign)
	}

	return varAssigns, nil
}

// Takes the list of variable assignments in a /etc/defaukt/grub file and looks for the assignment to the variables that
// matches the provided name.
func findDefaultGrubFileVarAssign(varAssigns []defaultGrubFileVarAssign, name defaultGrubFileVarName,
) (defaultGrubFileVarAssign, error) {
	for _, varAssign := range varAssigns {
		if varAssign.Name == string(name) {
			return varAssign, nil
		}
	}

	err := fmt.Errorf("failed to find %s variable assignment (%s)", installutils.GrubDefFile, name)
	return defaultGrubFileVarAssign{}, err
}

// Takes the string contents of a /etc/default/grub file and the name of the command-line args variable (either
// "GRUB_CMDLINE_LINUX" or "GRUB_CMDLINE_LINUX_DEFAULT") and returns a list of kernel command-line args.
//
// Params:
//   - defaultGrubFileContent: The string contents of the /etc/default/grub file.
//   - varName: The name of variable that contains kernel command-line args. Either "GRUB_CMDLINE_LINUX" or
//     "GRUB_CMDLINE_LINUX_DEFAULT".
//
// Returns:
//   - cmdLineVarAssign: The variable assignment that matches 'varName'.
//   - args: The list of kernel command-line args.
//   - insertAt: An index that new kernel command-line args can be inserted at.
func getDefaultGrubFileLinuxArgs(defaultGrubFileContent string, varName defaultGrubFileVarName,
) (defaultGrubFileVarAssign, []grubConfigLinuxArg, int, error) {
	varAssigns, err := findDefaultGrubFileVarAssigns(defaultGrubFileContent)
	if err != nil {
		err = fmt.Errorf("failed to parse %s file:\n%w", installutils.GrubDefFile, err)
		return defaultGrubFileVarAssign{}, nil, 0, err
	}

	// Find the variable's (e.g. GRUB_CMDLINE_LINUX) line.
	cmdLineVarAssign, err := findDefaultGrubFileVarAssign(varAssigns, varName)
	if err != nil {
		return defaultGrubFileVarAssign{}, nil, 0, err
	}

	// The (parsed) string value of the variable is copied verbatim into the grub.cfg file.
	// So, args can have quotes if needed, but those quotes will be double escaped.
	argsString := cmdLineVarAssign.Value
	grubTokens, err := grub.TokenizeConfig(argsString)
	if err != nil {
		err = fmt.Errorf("failed to parse %s's value:\n%w", varName, err)
		return defaultGrubFileVarAssign{}, nil, 0, err
	}

	var insertAt int
	if varName == defaultGrubFileVarNameCmdlineLinuxDefault {
		// GRUB_CMDLINE_LINUX_DEFAULT variable has the $kernelopts arg.
		// Any args inserted should be inserted before $kernelopts.
		insertAt, err = findCommandLineInsertAt(grubTokens, true /*requireKernelOpts*/)
		if err != nil {
			err = fmt.Errorf("failed to parse %s's value args:\n%w", varName, err)
			return defaultGrubFileVarAssign{}, nil, 0, err
		}
	} else {
		// Insert args at the end of the string.
		insertAt = len(argsString)
	}

	args, err := ParseCommandLineArgs(grubTokens)
	if err != nil {
		err = fmt.Errorf("failed to parse %s's value args:\n%w", varName, err)
		return defaultGrubFileVarAssign{}, nil, 0, err
	}

	return cmdLineVarAssign, args, insertAt, nil
}

// Takes the string contents of /etc/default/grub file and inserts the provided command-line args.
func AddExtraCommandLineToDefaultGrubFile(defaultGrubFileContent string, extraCommandLine string) (string, error) {
	cmdLineVarAssign, _, insertAt, err := getDefaultGrubFileLinuxArgs(defaultGrubFileContent,
		defaultGrubFileVarNameCmdlineLinuxDefault)
	if err != nil {
		return "", err
	}

	argsString := cmdLineVarAssign.Value

	// Add the extra command-line args.
	argsString = argsString[:insertAt] + " " + extraCommandLine + " " + argsString[insertAt:]

	// Rewrite GRUB_CMDLINE_LINUX_DEFAULT line.
	defaultGrubFileContent = replaceDefaultGrubFileVarAssign(defaultGrubFileContent, cmdLineVarAssign, argsString)
	return defaultGrubFileContent, nil
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
func updateDefaultGrubFileKernelCommandLineArgs(defaultGrubFileContent string, varName defaultGrubFileVarName,
	argsToRemove []string, newArgs []string,
) (string, error) {
	cmdLineVarAssign, args, insertAt, err := getDefaultGrubFileLinuxArgs(defaultGrubFileContent, varName)
	if err != nil {
		return "", err
	}

	value := cmdLineVarAssign.Value
	value, err = updateKernelCommandLineArgsHelper(value, args, insertAt, argsToRemove, newArgs)
	if err != nil {
		return "", err
	}

	// Rewrite GRUB_CMDLINE_LINUX line.
	defaultGrubFileContent = replaceDefaultGrubFileVarAssign(defaultGrubFileContent, cmdLineVarAssign, value)
	return defaultGrubFileContent, nil
}

// Takes the string contents of the /etc/default/grub file and rewrites one of the variable assignments lines.
//
// Params:
//   - defaultGrubContent: The string contents of the /etc/default/grub file.
//   - varAssign: The variable assignment statement to replace.
//   - newValue: The string value to assign to the variable.
func replaceDefaultGrubFileVarAssign(defaultGrubFileContent string, varAssign defaultGrubFileVarAssign, newValue string,
) string {
	// Rewrite the GRUB_CMDLINE_LINUX_DEFAULT line.
	cmdLineString := fmt.Sprintf("%s=%s", varAssign.Name, grub.ForceQuoteString(newValue))

	start := varAssign.Token.Loc.Start.Index
	end := varAssign.Token.Loc.End.Index

	// Rewrite the /etc/default/grub file.
	defaultGrubFileContent = defaultGrubFileContent[:start] + cmdLineString + defaultGrubFileContent[end:]
	return defaultGrubFileContent
}

func insertDefaultGrubFileVarAssign(defaultGrubFileContent string, insertAfterLine *grub.Line, varName string,
	newValue string,
) string {
	// Figure out where to insert the new line.
	insertAt := 0
	newlineBefore := false
	if insertAfterLine != nil {
		if insertAfterLine.EndToken != nil {
			insertAt = insertAfterLine.EndToken.Loc.End.Index
			newlineBefore = insertAfterLine.EndToken.Type == grub.SEMICOLON
		} else {
			// EOF follows the last variable assignment.
			insertAt = insertAfterLine.Tokens[len(insertAfterLine.Tokens)-1].Loc.End.Index
			newlineBefore = true
		}
	}

	// Create new variable assignment line string.
	lineString := fmt.Sprintf("%s=%s", varName, grub.ForceQuoteString(newValue))

	// Build new /etc/default/grub file contents.
	builder := strings.Builder{}
	builder.WriteString(defaultGrubFileContent[:insertAt])
	if newlineBefore {
		builder.WriteString("\n")
	}
	builder.WriteString(lineString)
	builder.WriteString("\n")
	builder.WriteString(defaultGrubFileContent[insertAt:])

	defaultGrubFileContent = builder.String()
	return defaultGrubFileContent
}

// Sets the value of a variable in the /etc/default/grub file, either replacing the existing variable value (if one
// exists) or adding a new one.
func UpdateDefaultGrubFileVariable(defaultGrubFileContent string, varName string, newValue string) (string, error) {
	varAssigns, err := findDefaultGrubFileVarAssigns(defaultGrubFileContent)
	if err != nil {
		err = fmt.Errorf("failed to parse %s file:\n%w", installutils.GrubDefFile, err)
		return "", err
	}

	found := false
	existingVarAssign := defaultGrubFileVarAssign{}
	for _, varAssign := range varAssigns {
		if varAssign.Name == varName {
			existingVarAssign = varAssign
			found = true
			break
		}
	}

	if found {
		defaultGrubFileContent = replaceDefaultGrubFileVarAssign(defaultGrubFileContent, existingVarAssign, newValue)
	} else {
		insertAfter := (*grub.Line)(nil)
		if len(varAssigns) > 1 {
			line := varAssigns[len(varAssigns)-1].Line
			insertAfter = &line
		}

		defaultGrubFileContent = insertDefaultGrubFileVarAssign(defaultGrubFileContent, insertAfter, varName, newValue)

	}

	return defaultGrubFileContent, nil
}

// Checks if the image uses grub-mkconfig.
func isGrubMkconfigEnabled(imageChroot *safechroot.Chroot) (bool, error) {
	grub2ConfigFile, err := ReadGrub2ConfigFile(imageChroot)
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
func readDefaultGrubFile(imageChroot safechroot.ChrootInterface) (string, error) {
	logger.Log.Debugf("Reading %s file", installutils.GrubDefFile)

	grub2ConfigFilePath := getDefaultGrubFilePath(imageChroot)

	// Read the existing grub.cfg file.
	grub2Config, err := file.Read(grub2ConfigFilePath)
	if err != nil {
		return "", fmt.Errorf("failed to read grub file (%s):\n%w", installutils.GrubDefFile, err)
	}

	return grub2Config, nil
}

// Writes the string contents of the /etc/default/grub file.
func WriteDefaultGrubFile(grub2Config string, imageChroot safechroot.ChrootInterface) error {
	logger.Log.Debugf("Writing %s file", installutils.GrubDefFile)

	grub2ConfigFilePath := getDefaultGrubFilePath(imageChroot)

	// Update grub.cfg file.
	err := file.Write(grub2Config, grub2ConfigFilePath)
	if err != nil {
		return fmt.Errorf("failed to write grub file (%s):\n%w", installutils.GrubDefFile, err)
	}

	return nil
}

func getDefaultGrubFilePath(imageChroot safechroot.ChrootInterface) string {
	return filepath.Join(imageChroot.RootDir(), installutils.GrubDefFile)
}
