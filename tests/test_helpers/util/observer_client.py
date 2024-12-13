# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

import asyncio, threading
from asyncua import Client
from target_server.target_server_dict import TargetServerList
from clients.event_subscription import ServiceEvents, SubHandler

class ObserverClient:

    def __init__(self):
        self.event_received = False
        self.timeout = 4

    async def observer_client(self, tar_server_url, iteration_time, service_browse_name):
        async with Client(url=tar_server_url, timeout = self.timeout) as client:
            target_server_list = TargetServerList(None, iteration_time, self.timeout)
            target_server = await target_server_list.get_target_server(tar_server_url, service_browse_name)
            handler = SubHandler(client, tar_server_url, True)
            event_subscription = ServiceEvents(client, iteration_time, handler, target_server.event_node)
            await event_subscription.subscribe_event_with_filter(service_browse_name, client)
            while self.event_received == False:
                self.event_received = handler.event_received
                print("wait for event")
                await asyncio.sleep(1)


    def start_observer_client_thread(self, tar_server_url, iteration_time, service_browse_name):
        client_thread = threading.Thread(target=self.start_observer_client, daemon=True, args=(tar_server_url, iteration_time, service_browse_name))
        client_thread.start()

    def start_observer_client(self, tar_server_url, iteration_time, service_browse_name):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.observer_client(tar_server_url, iteration_time, service_browse_name))