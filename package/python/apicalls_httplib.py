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

"""
This example uses Python's standard httplib module to make calls against the
  Splunk REST API. This example does not use any SDK libraries to access Splunk. (this example can used
  as a validation check to determine if an API call has failed due to SDK or due to Splunk platform.)
The example happens to retrieve a list of installed apps from a given
Splunk instance, but they could apply as easily to any other area of the REST
API.
"""

import urllib.parse
import ssl
from xml.etree import ElementTree
import http.client


def main():
    HOST = "localhost"
    PORT = 8089
    USERNAME = "admin"
    PASSWORD = "changed!"

    # Present credentials to Splunk and retrieve the session key
    connection = http.client.HTTPSConnection(HOST, PORT, context=ssl._create_unverified_context())
    body = urllib.parse.urlencode({'username': USERNAME, 'password': PASSWORD})
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Content-Length': str(len(body)),
        'Host': HOST,
        'User-Agent': "apicalls_httplib.py/1.0",
        'Accept': "*/*"
    }
    try:
        connection.request("POST", "/services/auth/login", body, headers)
        response = connection.getresponse()
    finally:
        print('')
    if response.status != 200:
        connection.close()
        raise Exception(f"{response.status} ({response.reason})")
    body = response.read()
    connection.close()

    sessionKey = ElementTree.XML(body).findtext("./sessionKey")

    # Now make the request to Splunk for list of installed apps
    connection = http.client.HTTPSConnection(HOST, PORT, context=ssl._create_unverified_context())
    headers = {
        'Content-Length': "0",
        'Host': HOST,
        'User-Agent': "a.py/1.0",
        'Accept': "*/*",
        'Authorization': f"Splunk {sessionKey}",
    }
    try:
        connection.request("GET", "/services/apps/local", "", headers)
        response = connection.getresponse()
    finally:
        print('')
    if response.status != 200:
        connection.close()
        raise Exception(f"{response.status} ({response.reason})")

    body = response.read()
    connection.close()
    data = ElementTree.XML(body)
    apps = data.findall("{http://www.w3.org/2005/Atom}entry/{http://www.w3.org/2005/Atom}title")
    for app in apps:
        print(app.text)


if __name__ == "__main__":
    main()
