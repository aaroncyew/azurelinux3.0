#!/bin/python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
import inspect
import re
from dateutil.parser import parse
from glob import glob
from junit_xml import TestSuite, TestCase
from os.path import basename

# Markers of package test for detecting pass/fail
PACKAGE_TEST_END_REGEX     = re.compile(r'(?<=msg=")====== CHECK DONE .*\. EXIT STATUS (\d+)')
PACKAGE_TEST_IGNORE_REGEX  = re.compile(r'msg="\+ echo')
PACKAGE_TEST_SKIP_REGEX    = re.compile(r'(?<=msg=")====== SKIPPING CHECK')
PACKAGE_TEST_START_REGEX   = re.compile(r'(?<=msg=")====== CHECK START')
PACKAGE_TEST_STATUS_INDEX  = 0

TEST_FILE_REGEX                 = re.compile(r'(.*/)*(.*)-(.*)-(.*?)(\.src.rpm.test.log)')
TEST_FILE_PACKAGE_NAME_INDEX    = 1
TEST_FILE_PACKAGE_VERSION_INDEX = 2
TEST_FILE_PACKAGE_RELEASE_INDEX = 3

class PipelineLogger:
    def log_debug(self, msg):
        '''
        Debug logger for the package test analyzer.
        '''
        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame, 2)
        caller = caller_frame[1][3]
        print(f"##[debug]PACKAGE_TESTS::{caller}::{msg}")


class PackageTestAnalyzer:
    '''
    Package test class to expose all the required functionality for parsing
    the Mariner package build logs.
    '''
    def __init__(self, logger):
        self.logger = logger


    def _get_package_details(self, log_path):
        '''
        Fetch the package details from the log filename
        '''
        matched_groups = TEST_FILE_REGEX.search(log_path).groups()
        package_name = matched_groups[TEST_FILE_PACKAGE_NAME_INDEX]
        version = f"{matched_groups[TEST_FILE_PACKAGE_VERSION_INDEX]}-{matched_groups[TEST_FILE_PACKAGE_RELEASE_INDEX]}"
        self.logger.log_debug(f"Package: {package_name}  Version: {version}")

        return package_name, version

    def _get_timestamp(self, line):
        '''
        Get the timestamp from the log. Time is converted to epoch time.
        '''
        try:
            timestamp = parse((line.split(" ")[0].split("=")[1]).replace('"', ''))
        except ValueError as err:
            self.logger.log_debug(f"Timestamp parsing failed. Line: '{line}'. Error: '{str(err)}'.")
            return None
        # return epoch time
        return timestamp.timestamp()

    def _get_test_status(self, status):
        '''
        Get the test status from the log.
        '''
        self.logger.log_debug("STATUS => {status}.")

        return "Pass" if status == "0" else "Fail"

    def _get_test_details(self, f):
        '''
        Check the package test status
        '''
        start_time = end_time = None
        status = "Not Supported"
        for line in f:
            line = line.strip("\n")
            if PACKAGE_TEST_IGNORE_REGEX.search(line):
                continue

            if PACKAGE_TEST_START_REGEX.search(line):
                self.logger.log_debug(line)
                start_time = self._get_timestamp(line)

            end_line_match = PACKAGE_TEST_END_REGEX.search(line)
            if end_line_match:
                self.logger.log_debug(line)
                end_time = self._get_timestamp(line)
                status = self._get_test_status(end_line_match.groups()[PACKAGE_TEST_STATUS_INDEX])
                break

            if PACKAGE_TEST_SKIP_REGEX.search(line):
                self.logger.log_debug(line)
                status = "Skipped"
                break
        if start_time != None and end_time == None:
            status = "Aborted"
        return status, start_time, end_time

    def _analyze_package_test_log(self, log_path):
        '''
        Scrape the package test log and detect the test status.
        '''
        start_time = end_time = status = None
        elapsed_time = 0
        with open(log_path, 'r') as f:
            status, start_time, end_time = self._get_test_details(f)

        if start_time != None and end_time != None:
            elapsed_time = end_time - start_time

        self.logger.log_debug(f"Status: {status}. Start time: {start_time}. End time: {end_time}.")
        return status, elapsed_time

    def _get_test_output(self, log_path):
        start_log = False
        contents = []
        with open(log_path, 'r') as f:
            for line in f:
                if PACKAGE_TEST_IGNORE_REGEX.search(line):
                    continue

                if PACKAGE_TEST_START_REGEX.search(line):
                    start_log = True

                if start_log:
                    contents.append(line)

                if PACKAGE_TEST_END_REGEX.search(line):
                    break
            f.close()
        return " ".join(contents)

    def _build_junit_test_case(self, package_name, status, time, log_path, test_name):
        stdout = None
        if status == "Fail":
            stdout = self._get_test_output(log_path)

        tc = TestCase(package_name, test_name, time, stdout)

        if status == "Pass":
            return tc

        if status == "Fail":
            tc.add_failure_info("TEST FAILED. CHECK ATTACHMENTS TAB FOR FAILURE LOG")
        elif status == "Skipped":
            tc.add_skipped_info("PACKAGE TEST SKIPPED")
        elif status == "Not Supported":
            tc.add_skipped_info("PACKAGE TEST NOT SUPPORTED")
        else:
            tc.add_error_info(status)

        return tc


    def scan_package_test_logs(self, logs_path, junit_xml_filename, test_name):
        '''
        Scan the RPM build log folder and generate the package test report.
        '''
        test_cases = []
        with open(junit_xml_filename, "w") as f:
            for log_path in glob(f"{logs_path}/*.src.rpm.test.log"):
                self.logger.log_debug(f"Processing : {basename(log_path)}")

                package_name, version = self._get_package_details(log_path)
                status, elapsed_time = self._analyze_package_test_log(log_path)
                test_cases.append(self._build_junit_test_case(package_name, status, elapsed_time, log_path, test_name))

                self.logger.log_debug(f"Package name: {package_name}. Version: {version}. Test status: {status}. Duration: {elapsed_time}.")

            test_suite = TestSuite(test_name, test_cases)
            TestSuite.to_file(f, [test_suite], prettyprint=True)


# Entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('mandatory arguments')

    parser.add_argument('-j', '--junit', action='store', required=False,
                        default="pkgtest_report_junit.xml", help="JUnit XML report filename")
    required_args.add_argument('-p', '--logs_path', action='store', required=True,
                        help="Path of the 'rpmbuild' log directory")
    parser.add_argument('-t', '--test_name', action='store', required=False,
                        default="Package-Test", help="High-level test name for display")

    args = parser.parse_args()

    # Custom logger for ptest to log debug messages
    logger = PipelineLogger()
    logger.log_debug(f"Path: {args.logs_path}")

    # Instantiate the ptest object and process the package test logs
    analyzer = PackageTestAnalyzer(logger)
    analyzer.scan_package_test_logs(args.logs_path, args.junit, args.test_name)
