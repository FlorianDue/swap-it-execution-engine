# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

from util.start_docker_compose import DockerComposeEnvironment
from asyncua import Client
from target_server.target_server_dict import TargetServerList
from execute_service.check_service_in_and_output import CheckServiceMethodArguments
import asyncio, unittest, time

class CheckServerBrowsing(unittest.TestCase):

    async def check_server_browsing(self, env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])):
        #env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])
        env.run_docker_compose()
        time.sleep(10)

        async with Client(url="opc.tcp://localhost:4080") as client:
            #add a server to the target server list and check if it was browsed correctly
            target_server = await TargetServerList(None, 0.001, 4).get_target_server("opc.tcp://localhost:4080",
                                                                                  "GetPartsFromWarehouse")
            #check browsenames
            for browsename, value in zip([target_server.implementation, target_server.explored, target_server.url,
                                          target_server.Module_Type_SubType_BrowseName.Name,
                                          target_server.add_queue_element_bn.Name,
                                          target_server.remove_queue_element_bn.Name],
                                         ["open62541", True, "opc.tcp://localhost:4080",
                                          "WarehouseModuleType", "add_queue_element", "remove_queue_element"]):
                self.assertEqual(browsename, value)
            # check nodeIds
            for node, value in zip([target_server.ServiceModuleType_instance_node, target_server.execution_node,
                                    target_server.queue_variable, target_server.service_queue,
                                    target_server.state_variable, target_server.service_object],
                                   ["WarehouseModule", "Services", "queue_variable", "ServiceQueue", "AssetState",
                                    "Services"]):
                self.assertEqual(str(await self.check_browse_name(node, client)), value)
            #check the method arguments of the service method
            await self.check_method_arguments(target_server, client)
            #input arguments
            #self.assertListEqual(target_server.Input_Arguments[0], ["order", "SWAP_Order"])
            #output arguments
            #self.assertEqual(target_server.Output_Arguments["OutputArgumentType"],
            #                 "ServiceExecutionAsyncResultDataType")
            #self.assertListEqual(target_server.Output_Arguments["AsyncArguments"][0], ["order", "SWAP_Order"])
            await client.disconnect()
        env.stop_docker_compose()
        await asyncio.sleep(10)
    async def check_method_arguments(self, target_server, client):
        target_server.Input_Arguments, target_server.Output_Arguments = await CheckServiceMethodArguments().browse_method_arguments(
            target_server.service_node, client, *await target_server.browse_result_data_type_nodes(client),
            target_server.event_node, "GetPartsFromWarehouse",
            await target_server.load_custom_data_types(target_server.implementation, client))

    async def check_browse_name(self, nodeId, client):
        node = client.get_node(nodeId)
        bn = await node.read_browse_name()
        return bn.Name

    def run_test(self, custom_data_types = None, env = None):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.check_server_browsing(env = env))


