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

"""A command line utility for interacting with Splunk KV Store Collections."""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.client import connect

from utils import parse


def main():
    opts = parse(sys.argv[1:], {}, ".env")
    opts.kwargs["owner"] = "nobody"
    opts.kwargs["app"] = "search"
    service = connect(**opts.kwargs)

    print("KV Store Collections:")
    for collection in service.kvstore:
        print(f"  {collection.name}")

    # Let's delete a collection if it already exists, and then create it
    collection_name = "example_collection"
    if collection_name in service.kvstore:
        service.kvstore.delete(collection_name)

    # Let's create it and then make sure it exists
    service.kvstore.create(collection_name)
    collection = service.kvstore[collection_name]

    # Let's make sure it doesn't have any data
    print(f"Should be empty: {json.dumps(collection.data.query())}")

    # Let's add some json data
    collection.data.insert(json.dumps({"_key": "item1", "somekey": 1, "otherkey": "foo"}))
    # Let's add data as a dictionary object
    collection.data.insert({"_key": "item2", "somekey": 2, "otherkey": "foo"})
    collection.data.insert(json.dumps({"somekey": 3, "otherkey": "bar"}))

    # Let's make sure it has the data we just entered
    print(f"Should have our data: {json.dumps(collection.data.query(), indent=1)}")

    # Let's run some queries
    print(f"Should return item1: {json.dumps(collection.data.query_by_id('item1'), indent=1)}")

    # Let's update some data
    data = collection.data.query_by_id("item2")
    data['otherkey'] = "bar"
    # Passing data using 'json.dumps'
    collection.data.update("item2", json.dumps(data))
    print(f"Should return item2 with updated data: {json.dumps(collection.data.query_by_id('item2'), indent=1)}")
    data['otherkey'] = "foo"
    # Passing data as a dictionary instance
    collection.data.update("item2", data)
    print(f"Should return item2 with updated data: {json.dumps(collection.data.query_by_id('item2'), indent=1)}")

    query = json.dumps({"otherkey": "foo"})
    print(f"Should return item1 and item2: {json.dumps(collection.data.query(query=query), indent=1)}")

    query = json.dumps({"otherkey": "bar"})
    print(
        f"Should return third item with auto-generated _key: {json.dumps(collection.data.query(query=query), indent=1)}")

    # passing query data as dict
    query = {"somekey": {"$gt": 1}}
    print(f"Should return item2 and item3: {json.dumps(collection.data.query(query=query), indent=1)}")

    # update accelerated_field of the kvstore
    collection.update_accelerated_field('ind1', {'a': -1})
    collection = service.kvstore[collection_name]
    print("accelerated fields.ind1 value: ", collection["accelerated_fields.ind1"])

    # update acl properties of the kvstore
    print("acl properties before update", collection.access)
    collection.acl_update(sharing="app", owner="nobody", **{"perms.read": "admin, nobody"})
    print("acl properties after update", collection.access)

    # Let's delete the collection
    collection.delete()


if __name__ == "__main__":
    main()
