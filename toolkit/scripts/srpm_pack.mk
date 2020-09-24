# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Contains:
#	- SRPM Packing


######## SRPM PACKING ########

# Options for SRPM_FILE_SIGNATURE_HANDLING:
# enforce - Source signatures must match those specified in a signatures file
# skip    - Do not check signatures
# update  - Check signatures and updating any mismatches in the signatures file
SRPM_FILE_SIGNATURE_HANDLING ?= enforce

local_specs = $(shell find $(SPECS_DIR)/ -type f -name '*.spec')
local_spec_dirs = $(foreach spec,$(local_specs),$(dir $(spec)))
local_sources = $(shell find $(SPECS_DIR)/ -name '*')

toolchain_spec_list = $(toolchain_build_dir)/toolchain_specs.txt

$(call create_folder,$(BUILD_DIR))
$(call create_folder,$(BUILD_SRPMS_DIR))
$(call create_folder,$(BUILD_DIR)/SRPM_packaging)

# General targets
.PHONY: toolchain-input-srpms input-srpms clean-input-srpms
input-srpms: $(BUILD_SRPMS_DIR)
toolchain-input-srpms: $(STATUS_FLAGS_DIR)/build_toolchain_srpms.flag

clean: clean-input-srpms
clean-input-srpms:
	rm -rf $(BUILD_SRPMS_DIR)
	rm -rf $(STATUS_FLAGS_DIR)/build_srpms.flag
	rm -rf $(BUILD_DIR)/SRPM_packaging

# The directory freshness is tracked with a status flag. The status flag is only updated when all SRPMs have been
# updated.
$(BUILD_SRPMS_DIR): $(STATUS_FLAGS_DIR)/build_srpms.flag
	@touch $@
	@echo Finished updating $@

ifeq ($(DOWNLOAD_SRPMS),y)
srpm_download_urls := $(SRPM_URL) $(SRPM_UPDATE_URL)

$(STATUS_FLAGS_DIR)/build_srpms.flag: $(local_specs) $(local_spec_dirs) $(SPECS_DIR)
	for spec in $(local_specs); do \
		spec_file=$${spec} && \
		srpm_file=$$(rpmspec -q $${spec_file} --srpm --define='with_check 1' --define='dist $(DIST_TAG)' --queryformat %{NAME}-%{VERSION}-%{RELEASE}.src.rpm) && \
		for url in $(srpm_download_urls); do \
			wget $${url}/$${srpm_file} \
				-O $(BUILD_SRPMS_DIR)/$${srpm_file} \
				--no-verbose \
				$(if $(TLS_CERT),--certificate=$(TLS_CERT)) \
				$(if $(TLS_KEY),--private-key=$(TLS_KEY)) \
				&& \
			touch $(BUILD_SRPMS_DIR)/$${srpm_file} && \
			break; \
		done || $(call print_error,Loop in $@ failed) ; \
		{ [ -f $(BUILD_SRPMS_DIR)/$${srpm_file} ] || \
			$(call print_error,Failed to download $${srpm_file});  } \
	done || $(call print_error,Loop in $@ failed) ; \
	touch $@

$(STATUS_FLAGS_DIR)/build_toolchain_srpms.flag: $(STATUS_FLAGS_DIR)/build_srpms.flag
	@touch $@
else
$(STATUS_FLAGS_DIR)/build_srpms.flag: $(chroot_worker) $(local_specs) $(local_spec_dirs) $(SPECS_DIR) $(go-srpmpacker)
	$(go-srpmpacker) \
		--dir=$(SPECS_DIR) \
		--output-dir=$(BUILD_SRPMS_DIR) \
		--source-url=$(SOURCE_URL) \
		--dist-tag=$(DIST_TAG) \
		--ca-cert=$(CA_CERT) \
		--tls-cert=$(TLS_CERT) \
		--tls-key=$(TLS_KEY) \
		--build-dir=$(BUILD_DIR)/SRPM_packaging \
		--signature-handling=$(SRPM_FILE_SIGNATURE_HANDLING) \
		--worker-tar=$(chroot_worker) \
		--log-file=$(LOGS_DIR)/pkggen/srpms/srpmpacker.log \
		--log-level=$(LOG_LEVEL)
	touch $@

$(STATUS_FLAGS_DIR)/build_toolchain_srpms.flag: $(toolchain_spec_list) $(go-srpmpacker)
	$(go-srpmpacker) \
		--dir=$(SPECS_DIR) \
		--output-dir=$(BUILD_SRPMS_DIR) \
		--source-url=$(SOURCE_URL) \
		--dist-tag=$(DIST_TAG) \
		--ca-cert=$(CA_CERT) \
		--tls-cert=$(TLS_CERT) \
		--tls-key=$(TLS_KEY) \
		--build-dir=$(BUILD_DIR)/SRPM_packaging \
		--signature-handling=$(SRPM_FILE_SIGNATURE_HANDLING) \
		--pack-list=$(toolchain_spec_list) \
		--log-file=$(LOGS_DIR)/toolchain/srpms/toolchain_srpmpacker.log \
		--log-level=$(LOG_LEVEL)
	touch $@
endif