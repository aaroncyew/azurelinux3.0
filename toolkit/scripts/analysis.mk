# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Contains:
#	- Generate list of built packages
#	- Run check for ABI changes of built packages.
#       - Run check for .so files version change of built packages.

# Requires DNF on Mariner / yum and yum-utils on Ubuntu.

SODIFF_OUTPUT_FOLDER=$(BUILD_DIR)/sodiff
RPM_BUILD_LOGS_DIR=$(LOGS_DIR)/pkggen/rpmbuilding
BUILD_SUMMARY_FILE=$(SODIFF_OUTPUT_FOLDER)/build-summary.csv
BUILT_PACKAGES_FILE=$(SODIFF_OUTPUT_FOLDER)/built-packages.txt
SODIFF_REPO_FILE=$(SCRIPTS_DIR)/sodiff/sodiff.repo
SODIFF_SCRIPT=$(SCRIPTS_DIR)/sodiff/mariner-sodiff.sh

clean: clean-sodiff

clean-sodiff:
	rm -rf $(BUILD_SUMMARY_FILE)
	rm -rf $(BUILT_PACKAGES_FILE)
	rm -rf $(SODIFF_OUTPUT_FOLDER)

.PHONY: built-packages-summary
built-packages-summary: $(BUILT_PACKAGES_FILE)

.PHONY: build-summary
build-summary: $(BUILD_SUMMARY_FILE)

# $(BUILT_PACKAGES_FILE): Generates a file containing a space-separated list of built RPM packages and subpackages.
$(BUILT_PACKAGES_FILE): $(BUILD_SUMMARY_FILE)
	cut -f2 --output-delimiter=" " $(BUILD_SUMMARY_FILE) > $(BUILT_PACKAGES_FILE)

# $(BUILD_SUMMARY_FILE): Generates a file containing 2 columns separated by a tab character:
# SRPM name and a space-separated list of RPM packages and subpackages generated by building the SRPM.
# Information is obtained from the build logs.
$(BUILD_SUMMARY_FILE): | $(RPM_BUILD_LOGS_DIR) $(SODIFF_OUTPUT_FOLDER)
	sed -nE -e 's#^.+level=info msg="Built \(([^\)]+)\) -> \[(.+)\].+#\1\t\2#p' $(RPM_BUILD_LOGS_DIR)/* > $(BUILD_SUMMARY_FILE)

$(RPM_BUILD_LOGS_DIR) $(SODIFF_OUTPUT_FOLDER):
	mkdir -p $@
	touch $@

# fake-built-packages-list: Generates a fake list of built packages by producing a file listing all present RPM files in the RPM directory.
.PHONY: fake-built-packages-list
fake-built-packages-list: | $(SODIFF_OUTPUT_FOLDER)
	touch $(RPM_BUILD_LOGS_DIR)
	touch $(BUILD_SUMMARY_FILE)
	find $(RPMS_DIR) -type f -name '*.rpm' -exec basename {} \; > $(BUILT_PACKAGES_FILE)

# sodiff-check: runs check in a mariner container. Each failed package will be listed in $(SODIFF_OUTPUT_FOLDER).
.SILENT .PHONY: sodiff-check

sodiff-check: $(BUILT_PACKAGES_FILE)
	<$(BUILT_PACKAGES_FILE) $(SODIFF_SCRIPT) $(RPMS_DIR)/ $(SODIFF_REPO_FILE) $(RELEASE_MAJOR_ID) $(SODIFF_OUTPUT_FOLDER)
	( file -b $(SODIFF_OUTPUT_FOLDER)/sodiff.txt | grep -q empty ) || ( cat $(SODIFF_OUTPUT_FOLDER)/summary.txt ; $(call print_error, $@ failed - see $(SODIFF_OUTPUT_FOLDER) for list of failed files.) )
	echo "SODIFF finished - no changes detected."
