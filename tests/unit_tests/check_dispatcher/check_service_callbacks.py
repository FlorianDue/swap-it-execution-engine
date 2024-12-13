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
from util.observer_client import ObserverClient
from target_server.target_server_dict import TargetServerList
from control_interface_highlevel import ControlInterface

class CheckServiceStartedDispatcherCallback(unittest.TestCase):

    #no tasks, literal input
    async def check_service_callback_with_default_task(self, custom_server_types = None, env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])):
        env.run_docker_compose()
        await asyncio.sleep(10)
        helper = Helper()
        service_name = "Milling"
        ee_url = "opc.tcp://localhost:4000"
        dr_url = "opc.tcp://localhost:8000"
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
            cb.add_control_interface(ControlInterface(server_instance, server, cb.service_execution_list, TargetServerList(server_instance, iteration_time, 4), dr_url, None, "opc.tcp://localhost:", iteration_time, True, 4))
            #start a client to observe the service call
            observer = ObserverClient()
            observer.start_observer_client_thread("opc.tcp://localhost:4071", iteration_time, service_name)
            #service callback
            service_uuid = str(uuid.uuid4())
            await cb.service_started_cb(service_name, service_uuid,
                                        [EngineOpcUaDataConverter().convert_to_opcua_struct(DemoScenarioStructureValues().swap_order, server_instance.custom_data_types, "SWAP_Order")],
                                        OrderedDict([('order', 'SWAP_Order')]))
            #wait until the service finished event of the milling service was observerd
            while observer.event_received == False:
                await asyncio.sleep(1)
            server_namespace = CheckServerNamespace(2)
            await server_namespace.start_client(ee_url, server.get_node(server.nodes.objects), True)
            found = False
            for i in server_namespace.objects:
                if str(i.Name) == str(cb.baseTaskuuid):
                    found = True
            self.assertEqual(True, found)
            self.assertEqual(str(server_instance.parameters.parameters[0].service_uuid), service_uuid)
            self.assertEqual(server_instance.parameters.parameters[0].context, str(cb.baseTaskuuid))
            #print("server_instance.parameters.parameters", server_instance.parameters.parameters)
            #self.assertEqual(server_instance.parameters.parameters[0].variables[0], 'order')
            #self.assertEqual(server_instance.parameters.parameters[0].type[0], "SWAP_Order")
            #self.assertEqual(server_instance.parameters.parameters[0].name, service_name)
            self.assertEqual(cb.control_interface.service_execution_list.services[0].service_uuid, service_uuid)
            self.assertEqual(cb.control_interface.service_execution_list.services[0].task_uuid, str(cb.baseTaskuuid))
            self.assertEqual(cb.control_interface.service_execution_list.services[0].completed, True)
            self.assertEqual(cb.control_interface.service_execution_list.services[0].service_name, "Milling")
            await server.stop()
        env.stop_docker_compose()
        await asyncio.sleep(10)
        return custom_server_types

    async def check_service_callback_with_ordinary_task(self, custom_server_types = None, env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])):
        env.run_docker_compose()
        await asyncio.sleep(10)
        helper = Helper()
        service_name = "Milling"
        ee_url = "opc.tcp://localhost:4000"
        dr_url = "opc.tcp://localhost:8000"
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
            cb.add_control_interface(ControlInterface(server_instance, server, cb.service_execution_list, TargetServerList(server_instance, iteration_time, 4), dr_url, None, "opc.tcp://localhost:", iteration_time, True, 4))
            #start a client to observe the service call
            observer = ObserverClient()
            observer.start_observer_client_thread("opc.tcp://localhost:4071", iteration_time, service_name)

            production_task_uuid = str(uuid.uuid4())
            task1_uuid = str(uuid.uuid4())
            # check if the default production task is set
            await cb.task_started_cb("productionTask", production_task_uuid, production_task_uuid, {}, [])
            self.assertEqual(cb.baseTaskuuid, production_task_uuid)
            # add a task that has a literal input value
            await cb.task_started_cb("task1", task1_uuid, production_task_uuid, OrderedDict([('order', 'SWAP_Order')]),
                                     [DemoScenarioStructureValues().swap_order])
            service_uuid = str(uuid.uuid4())
            await cb.service_started_cb(service_name, service_uuid,
                                        ['order'],
                                        OrderedDict([('order', 'SWAP_Order')]), task1_uuid)

            # wait until the service finished event of the milling service was observerd
            while observer.event_received == False:
                await asyncio.sleep(1)
            server_namespace = CheckServerNamespace(2)
            await server_namespace.start_client(ee_url, server.get_node(server.nodes.objects), True)
            target_ee_objects = [production_task_uuid, task1_uuid]
            for i in target_ee_objects:
                found = False
                for j in server_namespace.objects:
                    if str(j.Name) == str(i):
                        found = True
                self.assertEqual(True, found)
            self.assertEqual(str(server_instance.parameters.parameters[0].service_uuid), service_uuid)
            self.assertEqual(server_instance.parameters.parameters[0].context, str(task1_uuid))
            #self.assertEqual(server_instance.parameters.parameters[0].variables[0], 'order')
            #self.assertEqual(server_instance.parameters.parameters[0].type[0], "SWAP_Order")
            self.assertEqual(server_instance.parameters.parameters[0].name, service_name)
            self.assertEqual(cb.control_interface.service_execution_list.services[0].service_uuid, service_uuid)
            self.assertEqual(cb.control_interface.service_execution_list.services[0].task_uuid, str(task1_uuid))
            self.assertEqual(cb.control_interface.service_execution_list.services[0].completed, True)
            self.assertEqual(cb.control_interface.service_execution_list.services[0].service_name, "Milling")
            await server.stop()
        env.stop_docker_compose()
        return custom_server_types

    def check_service_started_callbacks_test_without_tasks(self, custom_data_types = None, env = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.check_service_callback_with_default_task(custom_server_types = custom_data_types, env = env))

    def check_service_started_callbacks_test_with_tasks(self, custom_data_types = None, env = None):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.check_service_callback_with_ordinary_task(custom_server_types = custom_data_types, env = env))

