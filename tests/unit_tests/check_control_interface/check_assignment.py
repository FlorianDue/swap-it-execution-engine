# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

import unittest, asyncio, time
from target_server.target_server_dict import TargetServerList
from execute_service.assign_agent import AssignAgent
from execution_engine_server import ExecutionEngineServer
from data_object.data_object_interaction import DataObject
from data_types.internal_data_converter import EngineOpcUaDataConverter
from util.start_docker_compose import DockerComposeEnvironment
from values.ee_structures import DemoScenarioStructureTypes

class CheckAssignment(unittest.TestCase):

    async def check_static_assignment(self,custom_data_types = None, env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])):
        env.run_docker_compose()
        time.sleep(10)
        service_browse_name = "GetPartsFromWarehouse"
        server_url = "opc.tcp://localhost:4080"
        iteration_time = 0.001
        types = DemoScenarioStructureTypes()
        if custom_data_types == None:
            #start a server and create the custom types
            ee_url = "opc.tcp://localhost:4001"
            server_instance = ExecutionEngineServer(execution_engine_server_url=ee_url, log_info=True,
                                                    iteration_time=iteration_time)
            await server_instance.init_server()
            server = await server_instance.start_server(types.structures, DataObject(EngineOpcUaDataConverter()))
            custom_data_types = server_instance.custom_data_types
        capa, _ = self.create_structures(custom_data_types, "ResourceAssignment",
                               {"job_resource":"opc.tcp://service_server:4080"},
                               "Milling_Capabilities", {"test_numeric": 5, "test_boolean": False})
        target_server_list = TargetServerList(None, iteration_time, 4)
        target_server = await target_server_list.get_target_server(server_url, service_browse_name)
        #create the assignment class
        assign_agent = AssignAgent(None, 4)
        #assign without existing target resource
        target_agent = await assign_agent.allocate_job_to_agent("Get", [[],[]], "opc.tcp://localhost:8000", None, custom_data_types)
        self.assertEqual(target_agent, None)
        # assign without capabilities
        target_agent = await assign_agent.allocate_job_to_agent("Milling", [[], []], "opc.tcp://localhost:8000", None,custom_data_types)
        self.assertEqual(target_agent, "opc.tcp://service_server:4071")
        #assign with capabilities
        target_agent = await assign_agent.allocate_job_to_agent("Milling", [["Literal"], [capa]], "opc.tcp://localhost:8000",None, custom_data_types)
        self.assertEqual(target_agent, "opc.tcp://service_server:4071")
            #todo assign with external agent
            #todo assign with capability from dlo
        env.stop_docker_compose()
        await asyncio.sleep(10)

    def create_structures(self, custom_types, assignment_structure, assign_kwargs, capability_structure, capa_kwargs):
        assign, capa = None, None
        for i in range(len(custom_types["Name"])):
            if str(custom_types["Name"][i]) == str(assignment_structure):
                assign = custom_types["Class"][i](assign_kwargs)
            if str(custom_types["Name"][i]) == str(capability_structure):
                 capa = custom_types["Class"][i](capa_kwargs)
            return assign, capa

    def check_assignment(self, custom_data_types, env = None):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.check_static_assignment(custom_data_types, env = env))
