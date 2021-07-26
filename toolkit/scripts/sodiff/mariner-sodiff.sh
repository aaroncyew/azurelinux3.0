#!/bin/bash

# Required binaries:
# rpm and dnf on Mariner
# yum and yum-utils on Ubuntu

rpms_folder="$1"
repo_file_path="$2"
mariner_version="$3"
sodiff_out_dir="$4"
sodiff_log_file="${sodiff_out_dir}/sodiff.log"

# Setup output dir
mkdir -p "$sodiff_out_dir"

# Prepare mariner/ubuntu compatibility calls

common_options="-c $repo_file_path --releasever $mariner_version"
current_os=$(cat /etc/os-release | grep ^ID | cut -d'=' -f2)
if [[ $current_os == mariner ]]; then
    # Mariner uses DNF repoquery command
    DNF_COMMAND=dnf
    # Cache RPM metadata
    >/dev/null dnf $common_options -y makecache
else
    # Ubuntu uses repoquery command from yum-utils
    DNF_COMMAND=
    # Cache RPM metadata
    # Ubuntu does not come with gpgcheck plugin for yum
    >/dev/null yum $common_options -y --nogpgcheck makecache
fi

# Empty the log file
echo > "$sodiff_log_file"

# Get packages from stdin
for rpmpackage in $(cat); do
    package_path=$(find "$rpms_folder" -name "$rpmpackage" -type f)
    package_provides=`2>/dev/null rpm -qP "$package_path" | grep -E '[.]so[(.]' `
    echo "Processing ${rpmpackage}..." >> "$sodiff_log_file"
    for sofile in $package_provides; do
        # Query local metadata for provides
        sos_found=$( $DNF_COMMAND repoquery $common_options --whatprovides $sofile | wc -l )
        if [[ $sos_found -eq 0 ]] ; then
            # SO file not found, meaning this might be a new .SO
            # or a new version of a preexisting .SO.
            # Check if the previous version exists in the database.

            # Remove version part from .SO file
            sofile_no_ver=$(echo "$sofile" | sed -E 's/[.]so[(.].+/.so/')

            # check for generic .so in the repo
            sos_found=$( $DNF_COMMAND repoquery $common_options --whatprovides "${sofile_no_ver}*" | wc -l )

            if ! [[ $sos_found -eq 0 ]] ; then
                # Generic version of SO was found.
                # This means it's a new version of a preexisting SO.

                # Log which packages depend on this functionality
                $DNF_COMMAND repoquery $common_options --whatrequires "${sofile_no_ver}*" | sed -E 's/[.][^.]+[.]src[.]rpm//' > "$sodiff_out_dir"/"require_${sofile}"
            fi
        fi
    done
done

# Obtain a list of unique packages to be updated
2>/dev/null cat "$sodiff_out_dir"/require* | sort -u > "$sodiff_out_dir"/sodiff.txt || true
