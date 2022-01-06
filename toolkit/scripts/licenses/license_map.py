#!/usr/bin/python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
import json
from pathlib import Path
import sys
from types import SimpleNamespace

from spec_source_attributions import get_spec_source, VALID_SOURCE_ATTRIBUTIONS, VALID_SOURCE_ATTRIBUTIONS_REGEX

spec_dir_exceptions = { "kubernetes-1.18.14", "kubernetes-1.18.17", "kubernetes-1.19.7", "kubernetes-1.19.9", "kubernetes-1.20.2", "kubernetes-1.20.5" }

# Expected Schema:
# class LicenseCollection:
#     header: str
#     table_headers: List[str]
#     licenses: List[License]
#
# class License:
#     origin: str
#     license: str
#     specs: List[str]

def generate_markdown(license_collection):
    res = []
    res.append(license_collection.header)
    res.append('')
    res.append('| ' + ' | '.join(license_collection.table_headers) + ' |')
    res.append('|' + '|'.join([' --- ' for _ in license_collection.table_headers]) + '|')

    for origin, details in license_collection.licenses.__dict__.items():
        details.specs.sort(key=str.lower)
        res.append('| {0} | {1} | {2} |'.format(origin, details.license, ' <br> '.join(details.specs)))
    
    return '\n'.join(res) + '\n'


def deserialize_json(json_file):
    return json.load(json_file, object_hook=lambda d: SimpleNamespace(**d))


def get_sorted_license_collection(license_collection):
    sorted_license_collection = license_collection
    for origin, details in license_collection.licenses.__dict__.items():
        sorted_license_collection[origin].specs = sorted(details.specs, key=str.lower)


def get_missing_specs(spec_directories, license_collection):
    specs_in_json = set()
    for license in license_collection.licenses:
        for spec in license.specs:
            specs_in_json.add(spec)
    
    specs_in_dir = set()
    specs_unknown_distro = set()
    updated_license_collection = get_sorted_license_collection(license_collection)

    for directory in spec_directories:
        specs_in_current_dir = set()
        for spec_path in directory.glob('**/*.spec'):
            spec_name = spec_path.stem
            specs_in_current_dir += spec_name

            distribution = get_spec_source(spec_path)
            if distribution is None:
                specs_unknown_distro += spec_name
            else:


        specs_in_dir = specs_in_dir.union(specs_in_current_dir)

    specs_not_in_json = specs_in_dir - specs_in_json 
    specs_not_in_dir =  specs_in_json - specs_in_dir
    specs_not_in_dir -= spec_dir_exceptions
    return specs_not_in_json, specs_not_in_dir, specs_unknown_distro, updated_license_collection


def print_specs_error(header_message, specs_list):
    if len(specs_list):
        print(header_message)
        for s in sorted(specs_list, key=str.lower):
            print('\t' + s)
        print()


def process_licenses(input_filename, output_filename, spec_directories, only_update):
    with open(input_filename, 'r') as input_file:
        license_collection = deserialize_json(input_file)

    with open(output_filename, 'r') as output_file:
        old_content = output_file.read()

    specs_not_in_json, specs_not_in_dir, specs_unknown_distro, updated_license_collection = get_missing_specs(spec_directories, license_collection)

    new_content = generate_markdown(updated_license_collection)
    with open(output_filename, 'w') as output_file:
        output_file.write(new_content)

    if only_update:
        return

    if len(specs_not_in_json) or len(specs_not_in_dir) or len(specs_unknown_distro) or old_content != new_content:
        print_specs_error("Specs present in spec directories that are not present in data file:", specs_not_in_json)
        print_specs_error("Specs present in data file that are not present in spec directories:", specs_not_in_dir)
        print_specs_error("Specs from unknown distributions:", specs_unknown_distro)

        if old_content != new_content:
            print("License map file is out of date.")

        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Processes spec license data, find missing entries, and regenerate license map file.')
    parser.add_argument('input_filename', type=Path, help='Path to data file with license data.')
    parser.add_argument('output_filename', type=Path, help='Path to license map markdown file.')
    parser.add_argument('spec_directories', type=Path, nargs='+', help='Directories containing specs.')
    parser.add_argument('--only_update', help='Does not perform a check, only updates the markdown file according to the input JSON.', action='store_true')
    p = parser.parse_args()
    process_licenses(p.input_filename, p.output_filename, p.spec_directories, p.only_update)
