# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
from control_interface.target_server.target_server import TargetServerInstance
import asyncio
import nest_asyncio

class TargetServerList:

    def __init__(self, server, iteration_time, timeout):
        self.server = server
        self.target_server_instances = []
        self.path_to_module_type = ["Types", "ObjectTypes", "BaseObjectType", "ModuleType"]
        self.has_subtype_id = "ns=0;i=45"
        self.has_typedef_id = "ns=0;i=40"
        self.path_to_service_execution_result_data_type = ["Types", "DataTypes", "BaseDataType", "Structure"]
        self.path_to_queue_variable = ["Queue", "ServiceQueue", "queue_variable"]
        self.path_to_service_queue = ["Queue", "ServiceQueue"]
        self.path_to_add_queue_element = ["Queue", "ServiceQueue", "add_queue_element"]
        self.path_to_remove_queue_element = ["Queue", "ServiceQueue", "remove_queue_element"]
        self.async_result = "ServiceExecutionAsyncResultDataType"
        self.sync_result = "ServiceExecutionSyncResultDataType"
        self.path_to_base_event_type = ["0:Types", "0:EventTypes", "0:BaseEventType"]
        self.swap_parent_event_type = "ServiceFinishedEventType"
        self.iteration_time = iteration_time
        self.timeout = timeout

    def start_explore_server_loop(self, target_server_url, service_browse_name):
        explore_server_loop = asyncio.new_event_loop()
        explore_server_loop.run_until_complete(self.add_target_server_to_list(target_server_url, service_browse_name))

    async def add_target_server_to_list(self, target_server_url, service_browse_name):
        target_server = TargetServerInstance(target_server_url, self, self.server, self.iteration_time, self.timeout)
        self.target_server_instances.append(target_server)
        await target_server.reveal_server_nodes(service_browse_name)
        for i in range(len(self.target_server_instances)):
            if(str(self.target_server_instances[i].url) == str(target_server_url)):
                self.target_server_instances[i].explored = True
        return target_server

    async def check_target_server_list(self, url):
        for i in range(len(self.target_server_instances)):
            if str(url) == (self.target_server_instances[i].url):
                return self.target_server_instances[i]

    async def get_target_server(self, tar_server_url, service_browse_name):
        target_server = await self.check_target_server_list(tar_server_url)
        if target_server == None:
            explore_server_loop = asyncio.new_event_loop()
            nest_asyncio.apply(explore_server_loop)
            target_server = explore_server_loop.run_until_complete(
                self.add_target_server_to_list(tar_server_url, service_browse_name))
        else:
            server_exoplored = False
            while (server_exoplored == False):
                server_exoplored = target_server.explored
                await asyncio.sleep(self.iteration_time)
        return target_server

