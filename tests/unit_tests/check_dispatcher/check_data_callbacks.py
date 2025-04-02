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
from check_execution_engine_logic.check_data_converter import CheckInternalDataConverter
from asyncua import ua

class CheckDataDispatcherCallback(unittest.TestCase):
    async def check_data_callback(self, custom_server_types = None, env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])):
        env.run_docker_compose()
        await asyncio.sleep(20)
        helper = Helper()
        ee_url = "opc.tcp://localhost:4000"
        iteration_time = 0.001
        # start an execution engine server with a data object
        custom_data, server_instance, server = await helper.run_execution_engine_server(custom_server_types,
                                                                                            iteration_time, ee_url)
        if custom_server_types == None:
            custom_server_types = server_instance.custom_data_types
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
            ordered_dict = OrderedDict([('order_id', 'number'), ('stand', 'Stand_Segment'), ('number_light_segments', 'number'),
                                                                                   ('segment_1', 'Light_Segment'), ('segment_2', 'Light_Segment'), ('color', 'number')])
            await cb.task_started_cb("task3", task3_uuid, task2_uuid, ordered_dict,
                                     [["order", "order_id"], ["order", "stand"], ["order", "number_light_segments"], ["order", "segments", "[0]"], ["order", "segments", "[1]"], ["order", "segments", "[0]", "color"]])
            server_namespace = CheckServerNamespace(2)
            await server_namespace.start_client(ee_url, server.get_node(
                ua.NodeId(Identifier=uuid.UUID(task3_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)), False)
            demo_vals = DemoScenarioStructureValues()
            target_values = [1000, demo_vals.stand_segment,
                             5, demo_vals.light_segment_1,
                             demo_vals.light_segment_2, 'red']
            check_converter = CheckInternalDataConverter()
            #request some variables from task 3
            ctr = 0
            for i in ordered_dict.items():
                check_converter.check_generated_engine_types(await cb.provide_parameter(str(i[0]), task3_uuid), target_values[ctr])
                ctr +=1
            target_val = DemoScenarioStructureValues().swap_order
            #request some variables from taks 2
            server_namespace.reset(2)
            await server_namespace.start_client(ee_url, server.get_node(
                ua.NodeId(Identifier=uuid.UUID(task2_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)), False)
            check_converter.check_generated_engine_types(await cb.provide_parameter("order", task2_uuid), target_val)
            #request some variables from taks 1
            server_namespace.reset(2)
            await server_namespace.start_client(ee_url, server.get_node(
                ua.NodeId(Identifier=uuid.UUID(task1_uuid), NamespaceIndex=2, NodeIdType=ua.NodeIdType.Guid)), False)
            check_converter.check_generated_engine_types(await cb.provide_parameter("test", task1_uuid), target_val)
            await server.stop()
        env.stop_docker_compose()
        await asyncio.sleep(20)
        return custom_server_types

    def check_data_callbacks_test(self, custom_data_types = None, env = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.check_data_callback(custom_server_types = custom_data_types, env = env))




