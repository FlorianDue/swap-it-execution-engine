# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

import unittest, asyncio, time, uuid
from util.start_docker_compose import DockerComposeEnvironment
from values.service_parameters import ServiceParameter
from target_server.target_server_dict import TargetServerList
from clients.queue_interaction import TargetServerQueue
from asyncua import Client


class QueueInteraction(unittest.TestCase):

    async def queue_interaction(self, env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])):
        #env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])
        env.run_docker_compose()
        time.sleep(10)
        service_browse_name = "GetPartsFromWarehouse"
        server_url = "opc.tcp://localhost:4080"
        iteration_time = 0.001
        # start client, connect to server and explore the server's namespace
        async with (Client(url=server_url) as client):
            target_server_list = TargetServerList(None, iteration_time, 4)
            target_server = await target_server_list.get_target_server(server_url, service_browse_name)
            queue = TargetServerQueue(iteration_time, client)
            id_dict = Identifier()
            for i in range(3):
                id_dict.ids["Service"].append(str(uuid.uuid4()))
                id_dict.ids["Client"].append(await queue.client_add_queue_element(target_server, id_dict.ids["Service"][i]))
            #the queue elements are added asynchronously, so give the serter time to add them
            time.sleep(5)
            #check if the elements where added correctly
            value = await client.get_node(target_server.queue_variable).read_value()
            id_dict_new = Identifier()
            for i in range(len(value)):
                matched = False
                for j in range(len(id_dict.ids["Client"])):
                    if (str(value[i].Client_Identifier) == str(id_dict.ids["Client"][j])
                            and str(value[i].Service_UUID) == str(id_dict.ids["Service"][j])):
                        matched = True
                        id_dict_new.ids["Service"].append(id_dict.ids["Service"][j])
                        id_dict_new.ids["Client"].append(id_dict.ids["Client"][j])
                self.assertEqual(matched, True)
            #remove queue elements
            for i in range(len(value)):
                await queue.wait_for_queue_position_one(target_server, id_dict.ids["Client"][i], id_dict.ids["Service"][i])
                await queue.client_remove_queue_element(target_server, id_dict.ids["Service"][i], id_dict.ids["Client"][i])
            time.sleep(5)
            value = await client.get_node(target_server.queue_variable).read_value()
            param = ServiceParameter(target_server.client_custom_data_types)
            queue_type = param.get_custom_type("Queue_Data_Type")(Client_Identifier=None, Service_UUID=None, Entry_Number=param.get_custom_type("Queue_State_Variable_Type")(0), Queue_Element_State=0, ProductId=None, ServiceParameter=None)
            self.assertEqual(value, queue_type)
        env.stop_docker_compose()
        await asyncio.sleep(10)

    def run_queue_interaction(self, env = None):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.queue_interaction(env = env))

class Identifier:

    def __init__(self):
        self.ids = {"Client":[], "Service":[]}

