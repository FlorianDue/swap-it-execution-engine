# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

import asyncio, unittest
from execute_service.assign_agent import AssignAgent
from data_types.internal_data_converter import EngineOpcUaDataConverter, OpcUaEngineDataConverter
from dispatcher_callbacks.cb_functions import DispatcherCallbackFunctions
from values.ee_structures import DemoScenarioStructureValues
from util.start_docker_compose import DockerComposeEnvironment
from util.execution_engine_server import Helper

class CheckServiceStartedInputFiltering(unittest.TestCase):
    #todo implement assignment agent filtering
    async def filter_from_literal_input(self, custom_server_types = None, env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])):
        env.run_docker_compose()
        await asyncio.sleep(10)
        helper = Helper()
        service_name = "Milling"
        ee_url = "opc.tcp://localhost:4000"
        iteration_time = 0.001
        # start an execution engine server with a data object
        custom_data, server_instance, server = await helper.run_execution_engine_server(custom_server_types,
                                                                                        iteration_time, ee_url)
        if custom_server_types == None:
            custom_server_types = custom_data
        else:
            server_instance.custom_data_types = custom_server_types

        async with server:
            converter = EngineOpcUaDataConverter()
            struct_values = DemoScenarioStructureValues()
            cb = DispatcherCallbackFunctions(server, server_instance, converter,
                                         OpcUaEngineDataConverter())
            #create dummy input arguments (as OPC UA Types)
            input_parameter = [converter.convert_to_opcua_struct(struct_values.swap_order, server_instance.custom_data_types, "SWAP_Order"),
                               converter.convert_to_opcua_struct(struct_values.resource_assignment, server_instance.custom_data_types, "ResourceAssignment"),
                               converter.convert_to_opcua_struct(struct_values.capabilities, server_instance.custom_data_types, "Milling_Capabilities"),
                               converter.convert_to_opcua_struct(struct_values.assignment_agent, server_instance.custom_data_types, "AssignmentAgent"),
                               converter.convert_to_opcua_struct(struct_values.registry, server_instance.custom_data_types, "DeviceRegistry")]
            #check for a static resource assignment
            self.assertEqual(cb.callback_helpers.check_for_target_type(server_instance, input_parameter, "ResourceAssignment"), "opc.tcp://service_server:4080")
            #check for capabilities
            self.assertEqual(await AssignAgent(custom_server_types, 4).create_filter_agent_input_arguments([["test_name"], input_parameter], service_name, custom_server_types), ['Milling', ['test_numeric'], ['5']])
            #check for static assignment agent
            self.assertEqual(cb.callback_helpers.check_for_target_type(server_instance, input_parameter, "AssignmentAgent"), "opc.tcp://assignment_agent:10000")
            # check for static device_registry
            self.assertEqual(cb.callback_helpers.check_for_target_type(server_instance, input_parameter, "DeviceRegistry"), "opc.tcp://device_registry:8000")
            await server.stop()
        env.stop_docker_compose()
        await asyncio.sleep(10)
        return custom_server_types

    def run_test(self, custom_data_types = None, env = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.filter_from_literal_input(custom_data_types, env = env))
