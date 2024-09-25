# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# Contains:
#	- Toolchain Bootstrapping

######## TOOLCHAIN BOOTSTRAPPING ########

$(call create_folder,$(RPMS_DIR)/$(build_arch))
$(call create_folder,$(RPMS_DIR)/noarch)
$(call create_folder,$(SRPMS_DIR))
$(call create_folder,$(TOOLCHAIN_RPMS_DIR))

toolchain_build_dir = $(BUILD_DIR)/toolchain
toolchain_from_repos = $(toolchain_build_dir)/repo_rpms
toolchain_logs_dir = $(LOGS_DIR)/toolchain
toolchain_downloads_logs_dir = $(toolchain_logs_dir)/downloads
toolchain_downloads_manifest = $(toolchain_downloads_logs_dir)/download_manifest.txt
# populated_toolchain_chroot is the chroot where the toolchain is built, it is configured by the toolchain script
populated_toolchain_chroot = $(toolchain_build_dir)/populated_toolchain
populated_toolchain_rpms = $(populated_toolchain_chroot)/usr/src/mariner/RPMS
toolchain_spec_list = $(toolchain_build_dir)/toolchain_specs.txt
toolchain_spec_buildable_list = $(toolchain_build_dir)/toolchain_specs_buildable.txt
raw_toolchain = $(toolchain_build_dir)/toolchain_from_container.tar.gz
final_toolchain = $(toolchain_build_dir)/toolchain_built_rpms_all.tar.gz
toolchain_status_flag = $(STATUS_FLAGS_DIR)/build_toolchain.flag
toolchain_summary_file = $(STATUS_FLAGS_DIR)/build_toolchain_summary.txt

TOOLCHAIN_MANIFEST ?= $(TOOLCHAIN_MANIFESTS_DIR)/toolchain_$(build_arch).txt
# Find the *.rpm corresponding to each of the entries in the manifest
# regex operation: (.*\.([^\.]+)\.rpm) extracts *.(<arch>).rpm" to determine
# the exact path of the required rpm
# Outputs: $(TOOLCHAIN_RPMS_DIR)/<arch>/<name>.<arch>.rpm
sed_regex_full_path = 's`(.*\.([^\.]+)\.rpm)`$(TOOLCHAIN_RPMS_DIR)/\2/\1`p'
sed_regex_full_path_out_rpms = 's`(.*\.([^\.]+)\.rpm)`$(RPMS_DIR)/\2/\1`p'
toolchain_rpms := $(shell sed -nr $(sed_regex_full_path) < $(TOOLCHAIN_MANIFEST))
toolchain_rpms_buildarch := $(shell grep $(build_arch) $(TOOLCHAIN_MANIFEST))
toolchain_rpms_noarch := $(shell grep noarch $(TOOLCHAIN_MANIFEST))
toolchain_out_rpms := $(shell sed -nr $(sed_regex_full_path_out_rpms) < $(TOOLCHAIN_MANIFEST))

$(call create_folder,$(toolchain_build_dir))
$(call create_folder,$(toolchain_downloads_logs_dir))
$(call create_folder,$(toolchain_from_repos))
$(call create_folder,$(populated_toolchain_chroot))
$(call create_folder,$(MISC_CACHE_DIR)/toolchain)

.PHONY: raw-toolchain toolchain clean-toolchain clean-toolchain-containers check-manifests check-aarch64-manifests check-x86_64-manifests
##help:target:raw-toolchain=Build the initial toolchain bootstrap stage.
raw-toolchain: $(raw_toolchain)
##help:target:toolchain=Ensure all toolchain RPMs are present.
toolchain: $(toolchain_rpms)

clean: clean-toolchain

clean-toolchain: clean-toolchain-rpms
	$(SCRIPTS_DIR)/safeunmount.sh "$(toolchain_build_dir)"
	rm -rf $(toolchain_build_dir)
	rm -rf $(toolchain_logs_dir)
	rm -rf $(toolchain_from_repos)
	rm -rf $(toolchain_status_flag)
	rm -f $(SCRIPTS_DIR)/toolchain/container/toolchain-local-wget-list
	rm -f $(SCRIPTS_DIR)/toolchain/container/texinfo-perl-fix.patch
	rm -f $(SCRIPTS_DIR)/toolchain/container/Awt_build_headless_only.patch
	rm -f $(SCRIPTS_DIR)/toolchain/container/check-system-ca-certs.patch
	rm -f $(SCRIPTS_DIR)/toolchain/container/rpm-define-RPM-LD-FLAGS.patch
	rm -f $(SCRIPTS_DIR)/toolchain/container/.bashrc

# Clean the containers we use during toolchain build
ifeq ($(CLEAN_TOOLCHAIN_CONTAINERS),y)
clean:  clean-toolchain-containers
endif

# Optionally remove all toolchain docker containers
clean-toolchain-containers:
	$(SCRIPTS_DIR)/toolchain/toolchain_clean.sh $(BUILD_DIR)

clean-toolchain-rpms:
	for f in $(toolchain_rpms_buildarch); do rm -vf $(RPMS_DIR)/$(build_arch)/$$f; done
	for f in $(toolchain_rpms_noarch); do rm -vf $(RPMS_DIR)/noarch/$$f; done
	rm -rf $(TOOLCHAIN_RPMS_DIR)

clean-toolchain-cache:
	rm -rf $(MISC_CACHE_DIR)/toolchain

# Files to track when building the raw bootstrapped toolchain
bootstrap-hashing-list = \
	$(SCRIPTS_DIR)/toolchain/create_toolchain_in_container.sh \
	$(SCRIPTS_DIR)/toolchain/container/toolchain-sha256sums \
	$(SCRIPTS_DIR)/toolchain/container/Dockerfile \
	$(SCRIPTS_DIR)/toolchain/container/go14_bootstrap_aarch64.patch \
	$(call shell_real_build_only, find $(SCRIPTS_DIR)/toolchain/container/ -name *.sh)

# Files to track when building the official toolchain
official-hashing-list = \
	$(SCRIPTS_DIR)/toolchain/build_mariner_toolchain.sh \
	$(SCRIPTS_DIR)/toolchain/build_official_toolchain_rpms.sh \
	$(raw_toolchain)

ifeq ($(REBUILD_TOOLCHAIN),y)
# If we are rebuilding, we need srpms
$(toolchain_status_flag): $(STATUS_FLAGS_DIR)/build_toolchain_srpms.flag
# And also the toolchain scripts and other files
$(toolchain_status_flag): $(bootstrap-hashing-list) $(official-hashing-list)
endif

# raw_toolchain has no recipe, it is created by the toolchain builder. Just need to track it as a dependency via a no-op.
$(raw_toolchain): ;

toolchain_mode=auto
DISABLE_CACHE?=n

# Old varaibles
ifeq ($(INCREMENTAL_TOOLCHAIN)$(REBUILD_TOOLCHAIN),yy)
toolchain_mode=fast
else ifeq ($(REBUILD_TOOLCHAIN),y)
toolchain_mode=always
else ifeq ($(REBUILD_TOOLCHAIN),n)
toolchain_mode=never
endif

# New variables
ifeq ($(REBUILD_TOOLCHAIN),auto)
toolchain_mode=auto
endif
ifeq ($(REBUILD_TOOLCHAIN),always)
toolchain_mode=always
endif
ifeq ($(REBUILD_TOOLCHAIN),never)
toolchain_mode=never
endif
ifeq ($(REBUILD_TOOLCHAIN),fast)
toolchain_mode=fast
endif

.SILENT: $(toolchain_rpms) $(toolchain_out_rpms)
$(toolchain_rpms): $(toolchain_status_flag)
ifneq ($(REBUILD_TOOLCHAIN),never)
$(toolchain_out_rpms): $(toolchain_status_flag)
# If we are rebuilding, we need srpms
$(toolchain_status_flag): $(STATUS_FLAGS_DIR)/build_toolchain_srpms.flag
# And also the toolchain scripts and other files
$(toolchain_status_flag): $(bootstrap-hashing-list) $(official-hashing-list)
# If we are rebuilding the toolchain, we also expect the built RPMs to end up in out/RPMS
toolchain: $(toolchain_out_rpms)
endif

# Update time timestamps for toolchain rpms if the recipe is run
$(toolchain_rpms) $(toolchain_out_rpms):
	touch $@

#$(if $(filter y,$(INCREMENTAL_TOOLCHAIN)),--bootstrap-incremental-toolchain)
#$(if $(filter y,$(INCREMENTAL_TOOLCHAIN)),--official-build-incremental-toolchain)
.PHONY: always-run-toolchain-builder
$(toolchain_status_flag): $(no_repo_acl) $(go-toolchain) $(go-bldtracker) $(depend_REBUILD_TOOLCHAIN) $(depend_TOOLCHAIN_ARCHIVE) always-run-toolchain-builder
	$(go-toolchain) \
		--toolchain-rpms-dir="$(TOOLCHAIN_RPMS_DIR)" \
		--toolchain-manifest="$(TOOLCHAIN_MANIFEST)" \
		--log-level=$(LOG_LEVEL) \
		--log-file=$(LOGS_DIR)/toolchain/toolchain-builder.log \
		--download-manifest=$(toolchain_downloads_manifest) \
		$(foreach baseUrl, $(PACKAGE_URL_LIST),--package-urls="$(baseUrl)" ) \
		$(if $(TLS_CERT),--tls-cert="$(TLS_CERT)") \
		$(if $(TLS_KEY),--tls-key="$(TLS_KEY)") \
		--cache-dir="$(MISC_CACHE_DIR)/toolchain" \
		$(if $(TOOLCHAIN_ARCHIVE),--existing-archive="$(TOOLCHAIN_ARCHIVE)") \
		$(if $(filter y,$(DISABLE_CACHE)),--disable-cache) \
		--specs-dir="$(SPECS_DIR)" \
		\
		--rebuild=$(toolchain_mode) \
		--summary-file="$(toolchain_summary_file)" \
		\
		--bootstrap-output-file="$(raw_toolchain)" \
		--bootstrap-script="$(SCRIPTS_DIR)/toolchain/create_toolchain_in_container.sh" \
		--bootstrap-working-dir="$(SCRIPTS_DIR)/toolchain" \
		--bootstrap-build-dir="$(BUILD_DIR)" \
		--bootstrap-source-url="$(SOURCE_URL)" \
		$(foreach file, $(bootstrap-hashing-list),--bootstrap-input-files="$(file)" ) \
		\
		--official-build-output-file="$(final_toolchain)" \
		--official-build-script="$(SCRIPTS_DIR)/toolchain/build_mariner_toolchain.sh" \
		--official-build-working-dir="$(SCRIPTS_DIR)/toolchain" \
		--official-build-dist-tag="$(DIST_TAG)" \
		--official-build-build-number="$(BUILD_NUMBER)" \
		--official-build-release-version="$(RELEASE_VERSION)" \
		--official-build-build-dir="$(BUILD_DIR)" \
		--official-build-rpms-dir="$(RPMS_DIR)" \
		--official-build-specs-dir="$(SPECS_DIR)" \
		$(if $(filter y,$(RUN_CHECK)),--official-build-run-check) \
		--official-build-intermediate-srpms-dir="$(BUILD_SRPMS_DIR)" \
		--official-build-srpms-dir="$(SRPMS_DIR)" \
		--official-build-toolchain-from-repos="$(toolchain_from_repos)" \
		--official-build-bld-tracker="$(go-bldtracker)" \
		--official-build-timestamp-file="$(TIMESTAMP_DIR)/build_mariner_toolchain.jsonl" \
		$(foreach file, $(official-hashing-list),--official-input-files="$(file)" ) && \
	if [ ! -f $@ ] || [ -s $(toolchain_summary_file) ]; then \
		touch $@; \
	fi
