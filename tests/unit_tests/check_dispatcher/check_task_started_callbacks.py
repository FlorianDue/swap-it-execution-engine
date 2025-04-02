# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

import unittest, asyncio, uuid
from collections import OrderedDict
from data_types.internal_data_converter import EngineOpcUaDataConverter, OpcUaEngineDataConverter
from dispatcher_callbacks.cb_functions import DispatcherCallbackFunctions
from values.ee_structures import DemoScenarioStructureValues
from util.start_docker_compose import DockerComposeEnvironment
from util.server_explorer import CheckServerNamespace
from util.execution_engine_server import Helper
from asyncua import ua

class CheckTaskStartedDispatcherCallback(unittest.TestCase):

    async def check_task_started_callbacks(self, custom_server_types = None, env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])):
        env.run_docker_compose()
        await asyncio.sleep(20)
        helper = Helper()
        #get custom types from a service server
        ee_url = "opc.tcp://localhost:4000"
        iteration_time = 0.001
        #start an execution engine server with a data object
        custom_data_types, server_instance, server = await helper.run_execution_engine_server(custom_server_types, iteration_time, ee_url)
        if custom_server_types == None:
            custom_server_types = custom_data_types
        else:
            server_instance.custom_data_types = custom_server_types
        async with server:
            cb = DispatcherCallbackFunctions(server, server_instance, EngineOpcUaDataConverter(), OpcUaEngineDataConverter())
            production_task_uuid = str(uuid.uuid4())
            task1_uuid = str(uuid.uuid4())
            task2_uuid = str(uuid.uuid4())
            task_uuids = [production_task_uuid, task1_uuid, task2_uuid]
            #check if the default production task is set
            await cb.task_started_cb("productionTask", production_task_uuid, production_task_uuid, {}, [])
            self.assertEqual(cb.baseTaskuuid, production_task_uuid)
            #add a task that has a literal input value
            await cb.task_started_cb("task1", task1_uuid, production_task_uuid, OrderedDict([('order', 'SWAP_Order')]), [DemoScenarioStructureValues().swap_order])
            #add a second task that has a variable as input value
            await cb.task_started_cb("task2", task2_uuid, task1_uuid, OrderedDict([('order', 'SWAP_Order')]),
                                     ['order'])
            #check if the tasks were added correctly
            server_namespace = CheckServerNamespace(2)
            await server_namespace.start_client(ee_url, server.nodes.objects)
            helper.examine_browsing_results(task_uuids, server_namespace.objects)
            #check the task variables
            task_variable_names = ["TaskName", "StateVariable", "CurrentExecution", 'order']
            server_namespace.reset(2)
            await server_namespace.start_client(ee_url, server.get_node(
                ua.NodeId(Identifier=uuid.UUID(task2_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)))
            helper.examine_browsing_results(task_variable_names, server_namespace.variables)
            server_namespace.reset(2)
            await server_namespace.start_client(ee_url, server.get_node(
                ua.NodeId(Identifier=uuid.UUID(task1_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)), False)
            helper.examine_browsing_results(task_variable_names, server_namespace.variables)
            await server.stop()
        env.stop_docker_compose()
        await asyncio.sleep(20)
        return custom_server_types

    def check_task_started_callbacks_test(self, custom_data_types = None, env = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.check_task_started_callbacks(custom_server_types = custom_data_types, env = env))




