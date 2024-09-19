# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
from control_interface.clients.execution_client import ExecutionClient
import unittest, coverage, asyncio, time
from tests.test_helpers.util.start_docker_compose import DockerComposeEnvironment
from tests.test_helpers.values.ee_structures import DemoScenarioStructureValues, DemoScenarioStructureTypes
from execution_engine_logic.data_types.internal_data_converter import EngineOpcUaDataConverter, OpcUaEngineDataConverter
from execution_engine_logic.execution_engine_server import ExecutionEngineServer
from execution_engine_logic.data_object.data_object_interaction import DataObject
from execution_engine_logic.data_types.types import EngineArray, EngineStruct
from control_interface.control_interface import ControlInterface
from execution_engine_logic.service_execution.execution_dict import ServiceInfo, ExecutionList
from control_interface.target_server.target_server_dict import TargetServerList

ignore_files = "C:\Program Files\JetBrains\PyCharm 2024.1.3\plugins\python\helpers\pycharm\\"

class CheckExecutionClient(unittest.TestCase):

    async def check_execution_client(self, cov = coverage.Coverage(), custom_data_types = None):

        cov.start()
        env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])
        env.run_docker_compose()
        time.sleep(10)
        service_browse_name = "GetPartsFromWarehouse"
        server_url = "opc.tcp://localhost:4081"
        iteration_time = 0.001

        ee_url = "opc.tcp://localhost:4000"
        server_instance = ExecutionEngineServer(execution_engine_server_url=ee_url, log_info=True,
                                                iteration_time=iteration_time)
        await server_instance.init_server()
        types = DemoScenarioStructureTypes()
        server = await server_instance.start_server(types.structures, DataObject(EngineOpcUaDataConverter()))
        if custom_data_types == None:
            custom_data_types = server_instance.custom_data_types
        #server, server_instance, service_execution_list, target_server_list, device_registry_url, assignment_agent_url, docker, iteration_time, log_info):
        ci = ControlInterface(server_instance, server, ExecutionList(), TargetServerList(server_instance, iteration_time), None, None, True, iteration_time, True)
        #client list should be emtpy
        self.assertEqual(len(ci.client_dict["Client"]), 0)
        #init and check default clients
        ci.init_default_clients(3)
        self.assertEqual(len(ci.client_dict["Client"]), 3)

        ci.start_client_interaction(service_browse_name, None, [[], []], )

        # start new client since there are no in the execution list
        env.stop_docker_compose()
        cov.stop()
        cov.report(omit=[ignore_files + "_jb_runner_tools.py",
                         ignore_files + "_jb_serial_tree_manager.py",
                         ignore_files + "teamcity\common.py",
                         ignore_files + "teamcity\diff_tools.py",
                         ignore_files + "teamcity\messages.py",
                         ignore_files + "teamcity\\unittestpy.py",
                         "..\\docker_environment\\start_docker_compose.py"
                         ])
        return custom_data_types


    def test_check_assignment(self, cov = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.check_execution_client())





if __name__ == "__main__":
    unittest.main()