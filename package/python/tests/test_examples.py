#!/usr/bin/env python
#
# Copyright 2011-2015 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys
from subprocess import PIPE, Popen

import testlib


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
from splunklib import client

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
EXAMPLES_PATH = os.path.join(DIR_PATH, '..')


def check_multiline(testcase, first, second, message=None):
    """Assert that two multi-line strings are equal."""
    testcase.assertTrue(isinstance(first, str),
                        'First argument is not a string')
    testcase.assertTrue(isinstance(second, str),
                        'Second argument is not a string')
    # Unix-ize Windows EOL
    first = first.replace("\r", "")
    second = second.replace("\r", "")
    if first != second:
        testcase.fail(f"Multiline strings are not equal: {message}")


# Run the given python script and return its exit code.
def run(script, stdin=None, stdout=PIPE, stderr=None):
    process = start(script, stdin, stdout, stderr)
    process.communicate()
    return process.wait()


# Start the given python script and return the corresponding process object.
# The script can be specified as either a string or arg vector. In either case
# it will be prefixed to invoke python explicitly.
def start(script, stdin=None, stdout=PIPE, stderr=None):
    if isinstance(script, str):
        script = script.split()
    script = ["python3"] + script
    return Popen(script, stdin=stdin, stdout=stdout, stderr=stderr, cwd=EXAMPLES_PATH)


# Rudimentary sanity check for each of the examples
class ExamplesTestCase(testlib.SDKTestCase):
    def check_commands(self, *args):
        for arg in args:
            result = run(arg)
            self.assertEqual(result, 0, f'"{arg}" run failed with result code {result}')
        self.service.login()  # Because a Splunk restart invalidates our session

    def setUp(self):
        super().setUp()

        # Ignore result, it might already exist
        run("index.py create sdk-tests")

    def test_apicalls(self):
        run("apicalls_binding.py")
        run("apicalls_client.py")
        # run("apicalls_httplib.py")

    def test_binding1(self):
        result = run("binding1.py")
        self.assertEqual(result, 0)

    def test_conf(self):
        try:
            conf = self.service.confs['server']
            if 'SDK-STANZA' in conf:
                conf.delete("SDK-STANZA")
        except Exception as e:
            pass

        try:
            self.check_commands(
                "conf.py --help",
                "conf.py",
                "conf.py viewstates",
                'conf.py --app=search --owner=admin viewstates',
                "conf.py create server SDK-STANZA",
                "conf.py create server SDK-STANZA testkey=testvalue",
                "conf.py delete server SDK-STANZA")
        finally:
            conf = self.service.confs['server']
            if 'SDK-STANZA' in conf:
                conf.delete('SDK-STANZA')

    def test_event_types(self):
        self.check_commands(
            "event_types.py --help",
            "event_types.py")

    def test_export(self):
        self.check_commands("export.py --help")

    def test_fired_alerts(self):
        self.check_commands(
            "fired_alerts.py --help",
            "fired_alerts.py")

    def test_follow(self):
        self.check_commands("follow.py --help")

    def test_genevents(self):
        self.check_commands(
            "genevents.py --help",
            "genevents.py '_internal'")

    def test_get_job(self):
        self.check_commands("get_job.py")

    def test_index(self):
        self.check_commands(
            "index.py --help",
            "index.py",
            "index.py list")

    def test_info(self):
        self.check_commands(
            "info.py --help",
            "info.py")

    def test_inputs(self):
        self.check_commands(
            "inputs.py --help",
            "inputs.py")

    def test_job(self):
        self.check_commands(
            "job.py --help",
            "job.py",
            "job.py list",
            "job.py list @0")

    def test_kvstore(self):
        self.check_commands(
            "kvstore.py --help",
            "kvstore.py")

    def test_loggers(self):
        self.check_commands(
            "loggers.py --help",
            "loggers.py")

    def test_oneshot(self):
        self.check_commands(["oneshot.py", "search * | head 10"])

    def test_saved_search(self):
        temp_name = testlib.tmpname()
        self.check_commands(
            "saved_search.py",
            ["saved_search.py", "--help"],
            ["saved_search.py", "list-all"],
            ["saved_search.py", "--operation", "create", "--name", temp_name, "--search", "search * | head 5"],
            ["saved_search.py", "list", "--name", temp_name],
            ["saved_search.py", "list", "--operation", "delete", "--name", temp_name],
            ["saved_search.py", "list", "--name", "Errors in the last 24 hours"]
        )

    def test_saved_searches(self):
        self.check_commands(
            "saved_searches.py --help",
            "saved_searches.py")

    def test_search(self):
        self.check_commands(
            "search.py --help",
            ["search.py", "search * | head 10"],
            ["search.py", "search * | head 10 | stats count", "--output_mode", "csv"])

    def test_search_modes(self):
        self.check_commands("search_modes.py")

    def test_spcmd(self):
        self.check_commands(
            "spcmd.py --help",
            "spcmd.py -e\"get('authentication/users')\"")

    def test_spurl(self):
        self.check_commands(
            "spurl.py --help",
            "spurl.py",
            "spurl.py /services",
            "spurl.py apps/local")

    def test_stail(self):
        self.check_commands(["stail.py", "search index='_internal'"])

    def test_submit(self):
        self.check_commands("submit.py --help")

    def test_upload(self):
        # Note: test must run on machine where splunkd runs,
        # or a failure is expected
        if "SPLUNK_HOME" not in os.environ:
            self.skipTest("SPLUNK_HOME is not set, skipping")
        file_to_upload = os.path.expandvars(os.environ.get("INPUT_EXAMPLE_UPLOAD", "./upload.py"))
        self.check_commands(
            "upload.py --help",
            f"upload.py --index=sdk-tests {file_to_upload}")

    # The following tests are for the Analytics example
    def test_analytics(self):
        # We have to add the current path to the PYTHONPATH,
        # otherwise the import doesn't work quite right
        sys.path.append(EXAMPLES_PATH)
        import analytics

        # Create a tracker
        tracker = analytics.input.AnalyticsTracker(
            "sdk-test", self.opts.kwargs, index="sdk-test")

        service = client.connect(**self.opts.kwargs)

        # Before we start, we'll clean the index
        index = service.indexes["sdk-test"]
        index.clean(timeout=120)

        tracker.track("test_event", distinct_id="abc123", foo="bar", abc="123")
        tracker.track("test_event", distinct_id="123abc", abc="12345")

        # Wait until the events get indexed
        self.assertEventuallyTrue(lambda: index.refresh()['totalEventCount'] == '2', timeout=200)

        # Now, we create a retriever to retrieve the events
        retriever = analytics.output.AnalyticsRetriever(
            "sdk-test", self.opts.kwargs, index="sdk-test")

        # Assert applications
        applications = retriever.applications()
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0]["name"], "sdk-test")
        self.assertEqual(applications[0]["count"], 2)

        # Assert events
        events = retriever.events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["name"], "test_event")
        self.assertEqual(events[0]["count"], 2)

        # Assert properties
        expected_properties = {
            "abc": 2,
            "foo": 1
        }
        properties = retriever.properties("test_event")
        self.assertEqual(len(properties), len(expected_properties))
        for prop in properties:
            name = prop["name"]
            count = prop["count"]
            self.assertTrue(name in list(expected_properties))
            self.assertEqual(count, expected_properties[name])

        # Assert property values
        expected_property_values = {
            "123": 1,
            "12345": 1
        }
        values = retriever.property_values("test_event", "abc")
        self.assertEqual(len(values), len(expected_property_values))
        for value in values:
            name = value["name"]
            count = value["count"]
            self.assertTrue(name in list(expected_property_values))
            self.assertEqual(count, expected_property_values[name])

        # Assert event over time
        over_time = retriever.events_over_time(
            time_range=analytics.output.TimeRange.MONTH)
        self.assertEqual(len(over_time), 1)
        self.assertEqual(len(over_time["test_event"]), 1)
        self.assertEqual(over_time["test_event"][0]["count"], 2)

        # Now that we're done, we'll clean the index
        index.clean(timeout=120)


if __name__ == "__main__":
    os.chdir("..")
    import unittest

    unittest.main()
