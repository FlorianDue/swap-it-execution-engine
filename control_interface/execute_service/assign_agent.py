# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
from asyncua import Client
from control_interface.execute_service.default_assignment_agent import DefaultAssignmentAgent
import asyncio, nest_asyncio

class AssignAgent:

    def __init__(self, docker, timeout):
        self.assignment_loop = asyncio.new_event_loop()
        self.docker = docker
        self.timeout = timeout
        nest_asyncio.apply(self.assignment_loop)

    async def allocate_job_to_agent(self, service_browse_name, service_input_arguments, device_registry_url, assignment_agent_url, custom_data_types):
        filter_agent_method_arguments = await self.create_filter_agent_input_arguments(service_input_arguments, service_browse_name, custom_data_types)
        async with Client(url=device_registry_url, timeout = self.timeout) as client:
            agent_list = await self.get_agents_from_the_device_registry(client, filter_agent_method_arguments)
            await client.disconnect()
            if agent_list == None:
                return agent_list
        if(assignment_agent_url == None):
            resource = await DefaultAssignmentAgent(device_registry_url, agent_list, self.timeout).find_target_resource()
            if self.docker != None:
                resource = self.convert_to_custom_url(resource, self.docker)
            return resource
        else:
        #external assignment agend
            client = Client(url=assignment_agent_url, timeout = self.timeout)
            async with client:
                agent = await self.assign_service_to_resource(client, agent_list, device_registry_url)
                await client.disconnect()
            if self.docker != None:
                agent = self.convert_to_custom_url(agent, self.docker)
            return agent

    def convert_to_custom_url(self, resource, custom_url):
        resource = resource.split(":")
        return str(custom_url) + str(resource[len(resource) - 1])
    async def create_filter_agent_input_arguments(self, inp_args, service_browse_name, custom_data_types):
        capability_struct = self.get_capability_struct(str(service_browse_name) + "_Capabilities", custom_data_types)
        if capability_struct != None:
            names, values = [], []
            for i in range(len(inp_args[1])):
                if isinstance(inp_args[1][i], type(capability_struct)):
                    for key, val in inp_args[1][i].__dict__.items():
                        names.append(str(key))
                        values.append(str(val))
                    return [service_browse_name, names, values]
            else:
                return [service_browse_name, ["None"], ["None"]]
        else:
            return [service_browse_name, ["None"], ["None"]]

    async def assign_service_to_resource(self, client, agent_list, device_registry_url):
        browse_list = ["AssignmentModule", "Services"]
        current_node = await self.find_node_by_browsename_list(browse_list, client, None)
        agent = await current_node.call_method("2:assign_service", *[device_registry_url[10:], agent_list])
        return agent

    async def get_agents_from_the_device_registry(self, client, filter_agent_method_arguments):
        browse_list = ["AgentList", "PFDLServiceAgents"]
        current_node = await self.find_node_by_browsename_list(browse_list, client, None)
        agent_list = await current_node.call_method("1:Filter_Agents", *filter_agent_method_arguments)
        await client.disconnect()
        return agent_list

    async def find_node_by_browsename_list(self, browse_list, client, current_node):
        if current_node == None:
            current_node = client.get_objects_node()
        for i in range(len(browse_list)):
            children = await current_node.get_children()
            for child in children:
                bn = await child.read_browse_name()
                if (str(bn.Name) == str(browse_list[i])):
                    current_node = child
        return current_node

    def get_capability_struct(self, name, custom_data_types):
        for i in range(len(custom_data_types["Name"])):
            if(str(custom_data_types["Name"][i]) == name):
                return custom_data_types["Class"][i]()