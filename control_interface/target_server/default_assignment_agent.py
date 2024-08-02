# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
from asyncua import Client

class DefaultAssignmentAgent:

    def __init__(self, device_registry_url, agent_list):
        self.device_registry_url = device_registry_url
        self.agent_list = agent_list
        self.agents = {"NodeId":[], "QueueElements":[]}

    async def find_target_resource(self):
        async with Client(url=self.device_registry_url) as client:
            await client.load_type_definitions()
            for agent in self.agent_list:
                queue = await self.browse_children(client.get_node(agent))
                self.agents["NodeId"].append(agent)
                if isinstance(queue, list):
                    self.agents["QueueElements"].append(len(queue))
                else:
                    self.agents["QueueElements"].append(0)
            target_agent = await client.get_node(self.agents["NodeId"][self.agents["QueueElements"].index(min(self.agents["QueueElements"]))]).read_browse_name()
            return target_agent.Name

    async def browse_children(self, node):
        children = await node.get_children()
        for child in children:
            bn = await child.read_browse_name()
            if str(bn.Name) == str("queue_variable"):
                variable_value = await child.read_value()
                return variable_value
            else:
                variable_value = await self.browse_children(child)
                if variable_value != None:
                    return variable_value
