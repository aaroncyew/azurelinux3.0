// Copyright Microsoft Corporation.
// Licensed under the MIT License.

package customizationmacros

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/microsoft/azurelinux/toolkit/tools/internal/file"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/logger"
	"github.com/microsoft/azurelinux/toolkit/tools/internal/rpm"
)

const (
	// macro files to customize the installer and final images
	disableDocsMacroFile    = "macros.installercustomizations_disable_docs"
	disableLocalesMacroFile = "macros.installercustomizations_disable_locales"
)

var (
	customizationMacroHeaderComments = []string{
		"# This macro file was dynamically generated by the Azure Linux Toolkit image generator",
		"# based on the configuration used at image creation time.",
		"",
	}
	docComments []string = []string{
		"# This stops documentation files (anything fine in a package which is %%doc) from being installed.",
		"# To enable documentation files, remove this file, or comment out '%%_excludedocs 1'",
		"# Any packages which are already installed must be reinstalled for this change to take effect.",
	}
	localeComments []string = []string{
		"# This stops locale files from being installed. %%_install_langs acts as a filter for locales",
		"# which start with the provides strings. Setting it to an invalid value (ie 'POSIX') will",
		"# prevent any locale files from being installed.",
		"# To enable locale files, remove this file, or comment out '%%_install_langs POSIX'",
		"# Any packages which are already installed must be reinstalled for this change to take effect.",
	}
)

// addMacros adds the image custimization macros to the specified root directory.
func AddCustomizationMacros(rootDir string, disableDocs, disableLocales bool) (err error) {
	if disableDocs {
		logger.Log.Debugf("Disabling documentation packages")
		err = AddMacroFile(rootDir, rpm.DisableDocumentationDefines(nil), disableDocsMacroFile, docComments)
		if err != nil {
			return fmt.Errorf("failed to add disable docs macro file:\n%w", err)
		}
	}
	if disableLocales {
		logger.Log.Debugf("Disabling locale packages")
		err = AddMacroFile(rootDir, rpm.DisableLocaleDefines(nil), disableLocalesMacroFile, localeComments)
		if err != nil {
			return fmt.Errorf("failed to add disable locales macro file:\n%w", err)
		}
	}
	return nil
}

// validateComments checks that the comments are valid for a macro file: ie they are empty or start with '#'
func validateComments(comments []string) error {
	for _, comment := range comments {
		comment = strings.TrimSpace(comment)
		if !strings.HasPrefix(comment, "#") && comment != "" {
			return fmt.Errorf("extra comments must start with '#'(%s)", comment)
		}
	}
	return nil
}

func AddMacroFile(rootDir string, macros map[string]string, macroFileName string, extraComments []string) error {
	const macrosPath = "/usr/lib/rpm/macros.d"

	if len(macros) == 0 {
		return nil
	}

	header := customizationMacroHeaderComments
	if len(extraComments) > 0 {
		extraComments = append(extraComments, "")
		header = append(customizationMacroHeaderComments, extraComments...)
	}

	err := validateComments(extraComments)
	if err != nil {
		return fmt.Errorf("failed to validate extra comments while adding macro file:\n%w", err)
	}

	macroFilePath := filepath.Join(rootDir, macrosPath, macroFileName)
	err = os.MkdirAll(filepath.Dir(macroFilePath), os.ModePerm)
	if err != nil {
		return fmt.Errorf("failed to create directory for macro file:\n%w", err)
	}

	macroLines := []string{}
	for key, value := range macros {
		macroLines = append(macroLines, fmt.Sprintf("%%%s %s", key, value))
	}
	// Sort the lines to ensure the macro file is deterministic
	sort.Strings(macroLines)

	// Add the header, followed by any additional comments to the top of the file
	finalLines := append(header, macroLines...)
	err = file.WriteLines(finalLines, macroFilePath)
	if err != nil {
		return fmt.Errorf("failed to write macro file:\n%w", err)
	}
	return nil
}
