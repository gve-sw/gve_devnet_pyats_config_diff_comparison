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

#!/bin/env python

# To get a logger for the script
import logging

# To build the table at the end
from tabulate import tabulate

# Needed for aetest script
from ats import aetest
from ats.log.utils import banner

# Genie Imports
from genie.conf import Genie
from genie.abstract import Lookup

# import the genie libs
from genie.libs import ops # noqa

# Get your logger for your script
log = logging.getLogger(__name__)

# Needed if want to debug dictionaries
import json
# Configuration file
import test_params

import os, sys
from genie.utils.diff import Diff

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from env_var import device_commands, destinations, devices

import re


###################################################################
#                  COMMON SETUP SECTION                           #
###################################################################

class common_setup(aetest.CommonSetup):
    """ Common Setup section """

    # Connect to each device in the testbed
    @aetest.subsection
    def connect(self, testbed):
        # Get specified testbed
        genie_testbed = Genie.init(testbed)
        # Save in environment variables
        self.parent.parameters['testbed'] = genie_testbed
        device_list = []
        # Try connect one by one and save device objects in a list
        for device in genie_testbed.devices.values():
            # Only connect to the access and core devices
            if 'external' in device.name:
                continue
            log.info(banner(
                "Connect to device '{d}'".format(d=device.name)))
            try:
                device.connect(init_exec_commands=[], init_config_commands=[], log_stdout=False)
            except Exception as e:
                self.failed("Failed to establish connection to '{}'".format(
                    device.name))
            # Add device to list
            device_list.append(device)
        # Pass list of devices the to testcases
        self.parent.parameters.update(dev=device_list)

        #create directories if doesn't exist
        if not os.path.exists("./after"):
            os.makedirs("./after")
        if not os.path.exists("./diff"):
            os.makedirs("./diff")


###################################################################
#                     TESTCASES SECTION                           #
###################################################################

class ReachabilityTestcase(aetest.Testcase):
    def ping(self, device, destination):
        try:
            for dev in self.parent.parameters['dev']:
                if dev.name == device:
                    result = dev.ping(destination)

        except Exception as e:
            self.failed('Ping {} from device {} failed with error: {}'.format(
                                destination,
                                device,
                                str(e)
                            ))
        else:
            log.info(banner(f"Ping Results of {device}"))

            match = re.search(r'Success rate is (?P<rate>\d+) percent', result)
            success_rate = match.group('rate')

            log.info('Ping {} with success rate of {}%'.format(
                                        destination,
                                        success_rate,))

    @aetest.test.loop(source = devices, destinations = destinations)
    def ReachabilityTest(self, source, destinations):
        for destination in destinations:
            self.ping(source, destination)


# Test case definition, you can implement as many as you desire
class show_commands(aetest.Testcase):

    def general_test(self, command, excludes = []):
        failed_devices_list = []
        for dev in self.parent.parameters['dev']:
            # Check whether the command is part of the device_commands
            if not command.replace('_', ' ') in device_commands[dev.name]:
                continue

            before_file = json.load(open(f"./baseline/{command}_{dev.name}.json", "r"))

            after = dev.parse(command.replace('_', ' '))

            with open(f"./after/{command}_{dev.name}.json", "w") as json_file:
                json.dump(after, json_file, indent=2)

            after_file = json.load(open(f"./after/{command}_{dev.name}.json", "r"))

            dd = Diff(before_file, after_file, exclude=excludes)

            dd.findDiff()

            # if empty
            if not str(dd):
                continue

            try:
                log.warning(banner(f"Differences detected in {command}"))
                log.warning(f"There were differences detected in the following devices: {dev.name}")
                log.warning(str(dd))
                with open(f"./diff/{command}_{dev.name}.txt", "w") as diff_file:
                    diff_file.write(str(dd))
                failed_devices_list.append(dev.name)
            except:
                log.info(str(dd))

        return failed_devices_list

    @aetest.test
    def show_boot(self):
        command = "show_boot"
        failed_devices_list = self.general_test(command)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")

    @aetest.test 
    def show_inventory(self):
        command = "show_inventory"
        failed_devices_list = self.general_test(command)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")


    @aetest.test 
    def show_ip_arp(self):
        command = "show_ip_arp"
        excludes = ["age"]
        failed_devices_list = self.general_test(command, excludes=excludes)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")


    @aetest.test 
    def show_ip_interface_brief(self):
        command = "show_ip_interface_brief"
        failed_devices_list = self.general_test(command)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")


    @aetest.test 
    def show_ip_route(self):
        command = "show_ip_route"
        excludes = ["updated"]
        failed_devices_list = self.general_test(command, excludes=excludes)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")

    @aetest.test 
    def show_mac_addresstable(self):
        command = "show_mac_address-table"
        failed_devices_list = self.general_test(command)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")

    @aetest.test 
    def show_running_config(self):
        command = "show_running-config"
        excludes = ["Current configuration :"]
        failed_devices_list = self.general_test(command, excludes=excludes)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")

    @aetest.test
    def show_ip_bgp_neighbors(self):
        command = "show_ip_bgp_neighbors"
        excludes = ["current_time", "bgp_event_timer", "datagram", "received", "sent", "uptime", "delrcvwnd", "rcvnxt", 
        "receive_idletime", "sent_idletime", "sndnxt", "snduna", "sndwnd", "last_read", "last_write", "delrcvwnd", 
        "up_time", "rcvwnd", "last_received_refresh_end_of_rib", "last_received_refresh_start_of_rib"]
        failed_devices_list = self.general_test(command, excludes=excludes)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")


    @aetest.test
    def show_ip_ospf_database(self):
        command = "show_ip_ospf_database"
        excludes = ["age", "checksum", "seq_num"]
        failed_devices_list = self.general_test(command, excludes=excludes)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")

    @aetest.test
    def show_ip_bgp_summary(self):
        command = "show_ip_bgp_summary"
        excludes = ["msg_rcvd", "msg_sent", "up_down"]
        failed_devices_list = self.general_test(command, excludes=excludes)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")

    # @aetest.test
    # def show_log(self):
    #     command = "show_log"
    #     failed_devices_list = self.general_test(command)

    #     log.info(banner(f"Test Results of {command}"))

    #     if not failed_devices_list:
    #         self.passed("No difference between before and after ")
    #     else:
    #         self.failed(f"There were differences for the following devices: {failed_devices_list}")


    @aetest.test
    def show_ip_ospf_neighbor(self):
        command = "show_ip_ospf_neighbor"
        excludes = ["dead_time"]
        failed_devices_list = self.general_test(command, excludes=excludes)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")

    @aetest.test
    def show_version(self):
        command = "show_version"
        excludes = ["uptime", "uptime_this_cp"]
        failed_devices_list = self.general_test(command, excludes=excludes)

        log.info(banner(f"Test Results of {command}"))

        if not failed_devices_list:
            self.passed("No difference between before and after ")
        else:
            self.failed(f"There were differences for the following devices: {failed_devices_list}")


class InterfaceTestcase(aetest.Testcase):
    """ This is user Testcases section """

    @ aetest.test
    def check_interface_status(self):
        mega_dict = {}
        mega_tabular = []
        for dev in self.parent.parameters['dev']:
            mega_dict[dev.name] = {}
            log.info(banner("Gathering Interface Information from {}".format(
                dev.name)))
            output = dev.parse('show ip interface brief')
            for interface in output["interface"]:
                mega_dict[dev.name][interface] = {}
                mega_dict[dev.name][interface]["status"] = output["interface"][interface]["status"]
                mega_dict[dev.name][interface]["protocol"] = output["interface"][interface]["protocol"]
                smaller_tabular = []
                smaller_tabular.append(dev.name)
                smaller_tabular.append(interface)
                smaller_tabular.append(output["interface"][interface]["status"])
                smaller_tabular.append(output["interface"][interface]["protocol"])
                #review if condition to adjust to desired result
                if output["interface"][interface]["status"] == "administratively down":
                    smaller_tabular.append('Passed')
                elif ((output["interface"][interface]["status"] == "up" or 
                    output["interface"][interface]["protocol"] == "down") and
                    (output["interface"][interface]["status"] == "down")):
                    smaller_tabular.append('Failed')
                else:
                    smaller_tabular.append('Passed')
                mega_tabular.append(smaller_tabular)
        log.info(tabulate(mega_tabular,
                          headers = ['Interface', 'Status',
                                   'Protocol', 'Passed/Failed'],
                          tablefmt='orgtbl'))
        #review if condition to adjust to desired result
        for dev_name in mega_dict:
            for interface in mega_dict[dev_name]:
                if ((mega_dict[dev_name][interface]["status"] == "up" or 
                    mega_dict[dev_name][interface]["protocol"] == "down") and
                    (mega_dict[dev_name][interface]["status"] == "down")):
                    self.failed("{d}: {int} is in a not ok state, Status: {s} Protocol: {p}".format(
                        d=dev_name, int=interface, s=mega_dict[dev_name][interface]["status"], p=mega_dict[dev_name][interface]["protocol"]))
        self.passed("All interfaces are up or administratively down")

        
                
# #####################################################################
# ####                       COMMON CLEANUP SECTION                 ###
# #####################################################################


class common_cleanup(aetest.CommonCleanup):
    """ Common Cleanup for Sample Test """

    @aetest.subsection
    def clean_everything(self):
        """ Common Cleanup Subsection """
        log.info("Aetest Common Cleanup ")

        for dev in self.parent.parameters['dev']:
            log.info(f"Disconnecting from {dev.name} ")
            dev.disconnect()
            log.info(f"Successfully disconnected from {dev.name} ")


if __name__ == '__main__':  # pragma: no cover
    aetest.main()
