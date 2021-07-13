"""
Copyright (c) 2021 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

# Step 1: Specify the commands that you would like to test on the access devices
access_commands = [
    "show ip arp",
    "show ip interface brief",
    "show mac address-table",
    "show version",
    "show inventory",
    "show running-config",
    "show boot",
    "show ip route",
    "show ip ospf neighbor",
    "show ip ospf database"
]

# Step 2: Specify the commands that you would like to test on the access devices
core_commands = [
    "show ip arp",
    "show ip interface brief",
    "show mac address-table",
    "show version",
    "show inventory",
    "show running-config",
    "show boot",
    "show ip route",
    "show ip ospf neighbor",
    "show ip bgp summary",
    "show ip bgp neighbors",
    "show ip ospf database"
]

# Step 3: Create a dictionary with the devices as a key and the commands as the value
device_commands = {}

device_commands['access1'] = access_commands
device_commands['access2'] = access_commands
device_commands['core1'] = core_commands
device_commands['core2'] = core_commands

# Step 4: Specify all the devices that you would like to test in your topology
devices = ["access1", "access2", "core1", "core2"]

# Step 5: Specify the destinations that you would like to test for reachability
destinations = [
    [""], #access1
    [""], #access2
    [""], #core1
    [""]  #core2
]

# Step 6: Specify the testbed filename
testbed_filename = ''