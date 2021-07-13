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

from pyats.topology import loader
import os
import json
from env_var import device_commands, testbed_filename

# Load the testbed
testbed = loader.load(testbed_filename)

# Create a directory to store the baseline output
if not os.path.exists("baseline/"):
    os.makedirs("baseline/")

# Loop through the devices and obtain the respective commands
for device_name, commands in device_commands.items():
    device = testbed.devices[device_name]

    # In case a command fails, it will be added to the failed_commands list
    failed_commands = []

    # Connect to the device
    device.connect(init_exec_commands=[], init_config_commands=[], log_stdout=False)

    # Loop through the commands
    for command in commands:
        try:
            print(" ")
            print(f"We are printing the output of the following command {command}")
            
            # Parse the command using Genie parse
            output = device.parse(command)

            command_file_name = command.replace(' ', '_')

            # Write the output to a file in the baseline directory
            with open(f"./baseline/{command_file_name}_{device_name}.json", "w") as json_file:
                json.dump(output, json_file, indent=2)

            print(output)
            print(" ")
        except:
            print(f"Exception: We could not execute the following command {command}")
            failed_commands.append(command)

    print("-"*100)
    print(" ")
    # If there are failed commands, then print the commands
    if failed_commands:
        print("The following commands could not be parsed")
        for command in failed_commands:
            print(command)
    else:
        print(f"All commands were parsed successfully for {device_name}")

    # Disconnect from the device
    device.disconnect()