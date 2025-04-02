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

class CheckTaskFinishedDispatcherCallback(unittest.TestCase):
    async def check_task_finished_callback(self, custom_server_types = None, env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])):
        env.run_docker_compose()
        await asyncio.sleep(20)
        helper = Helper()
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
            cb = DispatcherCallbackFunctions(server, server_instance, EngineOpcUaDataConverter(),
                                             OpcUaEngineDataConverter())
            production_task_uuid = str(uuid.uuid4())
            task1_uuid = str(uuid.uuid4())
            task2_uuid = str(uuid.uuid4())
            task3_uuid = str(uuid.uuid4())
            # check if the default production task is set
            await cb.task_started_cb("productionTask", production_task_uuid, production_task_uuid, {}, [])
            helper.assertEqual(cb.baseTaskuuid, production_task_uuid)
            # add a task that has a literal input value
            await cb.task_started_cb("task1", task1_uuid, production_task_uuid, OrderedDict([('test', 'SWAP_Order')]),
                                     [DemoScenarioStructureValues().swap_order])
            # add a second task that has a variable as input value
            await cb.task_started_cb("task2", task2_uuid, task1_uuid, OrderedDict([('order', 'SWAP_Order')]),["test"])
            #add a third task, where only single values from the variable order are added
            await cb.task_started_cb("task3", task3_uuid, task2_uuid, OrderedDict([('order_id', 'number'), ('stand', 'Stand_Segment'), ('number_light_segments', 'number'),
                                                                                   ('segment_1', 'Light_Segment'), ('segment_2', 'Light_Segment'), ('color', 'number')]),
                                     [["order", "order_id"], ["order", "stand"], ["order", "number_light_segments"], ["order", "segments", "[0]"], ["order", "segments", "[1]"], ["order", "segments", "[0]", "color"]])
            server_namespace = CheckServerNamespace(2)
            await server_namespace.start_client(ee_url, server.get_node(
                ua.NodeId(Identifier=uuid.UUID(task3_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)), False)
            res_vars = ["order_id", "stand", "number_light_segments", "segment_1", "segment_2", "color"]
            helper.examine_browsing_results(res_vars, server_namespace.variables)
            value_check = [ua.QualifiedName(NamespaceIndex=2, Name='order_id'), ua.QualifiedName(NamespaceIndex=2, Name='number_light_segments'), ua.QualifiedName(NamespaceIndex=2, Name='color')]
            value_check_resuls = [1000, 5, "red"]
            #check the values of number and string variables
            for i in range(len(value_check)):
                node = await server_namespace.find_node_by_browsename(server.get_node(
                    ua.NodeId(Identifier=uuid.UUID(task3_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)), value_check[i])
                self.assertEqual(value_check_resuls[i], await server.get_node(node).read_value())
            # remove task 3 without parameters
            await cb.task_finished_cb("task3", task3_uuid, task2_uuid, [])
            #remove task 2 (with parameters handed over to task_1)
            await cb.task_finished_cb("task2", task2_uuid, task1_uuid, ['order'])
            server_namespace.reset(2)
            await server_namespace.start_client(ee_url, server.get_node(
                ua.NodeId(Identifier=uuid.UUID(task1_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)), False)
            target_variables = ['order', 'test']
            helper.examine_browsing_results(target_variables, server_namespace.variables)
            #remove task 1 with struct fields
            await cb.task_finished_cb("task1", task1_uuid, production_task_uuid, [["order", "order_id"], ["order", "stand"], ["order", "number_light_segments"], ["order", "segments", "[0]"], ["order", "segments", "[1]"], ["order", "segments", "[0]", "color"]])
            server_namespace.reset(2)
            await server_namespace.start_client(ee_url, server.get_node(
                ua.NodeId(Identifier=uuid.UUID(production_task_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)), False)
            for i in range(len(value_check)):
                node = await server_namespace.find_node_by_browsename(server.get_node(
                    ua.NodeId(Identifier=uuid.UUID(production_task_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)), value_check[i])
                self.assertEqual(value_check_resuls[i], await server.get_node(node).read_value())
            await cb.task_finished_cb("productionTask", production_task_uuid, production_task_uuid, [])
            await server.stop()
        env.stop_docker_compose()
        await asyncio.sleep(20)
        return custom_server_types

    def check_task_finished_callbacks_test(self, custom_data_types = None, env = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.check_task_finished_callback(custom_server_types = custom_data_types, env = env))




