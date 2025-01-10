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

"""A command line utility that prints out fired alerts."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.client import connect

from utils import parse


def main():
    opts = parse(sys.argv[1:], {}, ".env")
    service = connect(**opts.kwargs)

    for group in service.fired_alerts:
        header = f"{group.name} (count: {group.count})"
        print(header)
        print('=' * len(header))
        alerts = group.alerts
        for alert in alerts.list():
            content = alert.content
            for key in sorted(content.keys()):
                value = content[key]
                print(f"{key}: {value}")
            print()


if __name__ == "__main__":
    main()
