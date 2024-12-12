# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
import asyncio
from asyncua import ua, Client
from control_interface.execute_service.check_service_in_and_output import CheckServiceMethodArguments
from execution_engine_logic.service_execution.execution_results import ExecutionParameter

class TargetServerInstance:

    def __init__(self, url, target_server_list_browsepaths, server, iteration_time, timeout):
        self.server = server
        self.service_node = None
        self.service_idx = None
        self.execution_node = None
        self.Input_Arguments = None
        self.Output_Arguments = None
        self.service_object = None
        self.state_variable = None
        self.queue_variable = None
        self.service_queue = None
        self.add_queue_element_bn = None
        self.remove_queue_element_bn = None
        self.implementation = None
        self.HasSubtype_reference_nodeId = None
        self.client_custom_data_types = {"Name": [], "Class": []}
        self.url = url
        self.target_server_list_browsepaths = target_server_list_browsepaths
        self.service_arguments = None
        self.explored = False
        self.iteration_time = iteration_time
        self.timeout = timeout

    async def reveal_server_nodes(self, service_browse_name):
        async with Client(url=self.url, timeout = self.timeout) as client:
            build_information = client.get_node("ns=0;i=2256")
            impl = await build_information.read_value()
            stack = impl.BuildInfo.ManufacturerName
            self.implementation = str(stack) if str(stack) == 'open62541' else "python"
            self.client_custom_data_types = await self.load_custom_data_types(self.implementation, client)
            await self.browse_module_objects(client)
            await self.get_service_node(service_browse_name)
            self.event_node = await self.browse_event(client)
            await client.disconnect()

    async def match_service_input(self, dlo_service_input, client, custom_data_types, bn):
        self.service_arguments = CheckServiceMethodArguments()
        self.Input_Arguments, self.Output_Arguments = await self.service_arguments.browse_method_arguments(self.service_node, client, *await self.browse_result_data_type_nodes(client), self.event_node, bn, self.client_custom_data_types)
        service_parameter = await self.service_arguments.check_input_arguments(dlo_service_input, self.Input_Arguments, custom_data_types)
        return service_parameter

    async def browse_module_objects(self, client):
        self.HasSubtype_reference_nodeId = ua.NodeId.from_string(self.target_server_list_browsepaths.has_subtype_id)
        module_type_data_type_node = await self.browse_data_type_node_from_root(self.target_server_list_browsepaths.path_to_module_type, client)
        await self.browse_module_type(await module_type_data_type_node.get_references())
        await self.browse_ServiceModuleType_instance_node(client)
        self.queue_variable = await self.find_node_by_browsename_list(self.target_server_list_browsepaths.path_to_queue_variable, client, self.ServiceModuleType_instance_node)
        self.service_queue = await self.find_node_by_browsename_list( self.target_server_list_browsepaths.path_to_service_queue, client, self.ServiceModuleType_instance_node)
        add = await self.find_node_by_browsename_list( self.target_server_list_browsepaths.path_to_add_queue_element, client, self.ServiceModuleType_instance_node)
        self.add_queue_element_bn = await add.read_browse_name()
        remove = await self.find_node_by_browsename_list( self.target_server_list_browsepaths.path_to_remove_queue_element, client, self.ServiceModuleType_instance_node)
        self.remove_queue_element_bn = await remove.read_browse_name()
        module_type_children = await self.ServiceModuleType_instance_node.get_children()
        self.service_object = self.execution_node = await self.browse_children(module_type_children, "Services")
        bn = await self.service_object.read_browse_name()
        self.service_idx = bn.NamespaceIndex
        state_child = await self.browse_children(module_type_children, "State")
        self.state_variable = await self.browse_children(await state_child.get_children(), "AssetState")

    async def browse_module_type(self, references):
        for i in references:
            if i.IsForward == True:
                if str(i.ReferenceTypeId.Identifier) == str(self.HasSubtype_reference_nodeId.Identifier) \
                        and str(i.ReferenceTypeId.NamespaceIndex) == str(self.HasSubtype_reference_nodeId.NamespaceIndex):
                    self.Module_Type_SubType_BrowseName = i.BrowseName

    async def browse_ServiceModuleType_instance_node(self, client):
        object_node = client.get_objects_node()
        objects_children = await object_node.get_children()
        HasTypeDefinition_reference_nodeId = ua.NodeId.from_string(self.target_server_list_browsepaths.has_typedef_id)
        for i in objects_children:
            references = await i.get_references()
            for j in references:
                if j.IsForward == True:
                    if str(j.ReferenceTypeId.Identifier) == str(HasTypeDefinition_reference_nodeId.Identifier) \
                            and str(j.ReferenceTypeId.NamespaceIndex) == str(
                        HasTypeDefinition_reference_nodeId.NamespaceIndex) \
                            and str(self.Module_Type_SubType_BrowseName) == str(j.BrowseName):
                        self.ServiceModuleType_instance_node = i
                        # todo extend the browsing and identify the service. match the service the the
                        # service to be called to identify a concrete subtpe of the module type -> service matching,
                        # enable multiple subtypes of the  Module type in one information model!!!

    async def get_service_node(self, service_browse_name):
        children = await self.service_object.get_children()
        self.service_node  = await self.browse_children(children, service_browse_name)

    async def browse_children(self, node, target_child):
        for child in node:
            bn = await child.read_browse_name()
            if str(bn.Name) == target_child:
                return child

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

    async def browse_result_data_type_nodes(self, client):
        self.execution_node = await self.browse_data_type_node_from_root(self.target_server_list_browsepaths.path_to_service_execution_result_data_type, client)
        execution_data_type_children = await self.execution_node.get_children()
        for child in execution_data_type_children:
            child = client.get_node(child)
            child_bn = await client.get_node(child).read_browse_name()
            if str(child_bn.Name) == self.target_server_list_browsepaths.sync_result:
                self.service_server_sync_result_data_type_node_id = child
            if str(child_bn.Name) == self.target_server_list_browsepaths.async_result:
                self.service_server_async_result_data_type_node_id = child
        return self.service_server_sync_result_data_type_node_id, self.service_server_async_result_data_type_node_id

    async def browse_event(self, client):
        base_event_type_node = await client.nodes.root.get_child(self.target_server_list_browsepaths.path_to_base_event_type)
        even_types = await base_event_type_node.get_children()
        return await self.browse_children(even_types, self.target_server_list_browsepaths.swap_parent_event_type)

    async def browse_data_type_node_from_root(self, browse_name_list, client):
        current_node = client.get_root_node()
        node = None
        for i in range(len(browse_name_list)):
            node_children = await current_node.get_children()
            for node in node_children:
                node = client.get_node(node)
                node_bn = await node.read_browse_name()
                if str(node_bn.Name) == str(browse_name_list[i]):
                    current_node = node
                    break
        return node

    async def client_read_state_variable(self, client):
        while True:
            state_variable_node = client.get_node(self.state_variable)
            state_var_value = await state_variable_node.read_value()
            if state_var_value == 4:
                await state_variable_node.write_value(5, ua.VariantType.Int32)
                break
            else:
                await asyncio.sleep(self.iteration_time)

    async def client_load_custom_data_types_from_python_server(self, custom_type_definitions, client_custom_data_types):
        for name, obj in custom_type_definitions.items():
            client_custom_data_types["Name"].append(name)
            client_custom_data_types["Class"].append(obj)
        return client_custom_data_types

    async def client_load_custom_data_types_from_open62541_server(self, service_server_cust_data_types, client_custom_data_types):
        for i in service_server_cust_data_types:
            if isinstance(i, dict):
                for (name) in i.keys():
                    if name != 'ua' and name != 'datetime' and name != 'uuid' and name != 'IntEnum' \
                            and name != 'dataclass' and name != 'field' and name != 'List' and name != 'Optional' and name != '__builtins__':
                        client_custom_data_types["Name"].append(name)
                        client_custom_data_types["Class"].append(i[name])
        return client_custom_data_types

    async def load_custom_data_types(self, implementation, client):
        if implementation == "python":
            cust_enums = await client.load_enums()
            self.client_custom_data_types = await self.client_load_custom_data_types_from_python_server(cust_enums, self.client_custom_data_types)
            service_server_cust_data_types = await client.load_data_type_definitions()
            self.client_custom_data_types = await self.client_load_custom_data_types_from_python_server(service_server_cust_data_types, self.client_custom_data_types)
        elif implementation == "open62541":
            service_server_cust_data_types = await client.load_type_definitions()
            self.client_custom_data_types = await self.client_load_custom_data_types_from_open62541_server(service_server_cust_data_types, self.client_custom_data_types)
        return self.client_custom_data_types

    async def append_service_results(self, task_uuid, service_uuid, result, name):
        types, names, values = [], [], []
        for i in range(len(result["Variable_Name"])):
            names.append(result["Variable_Name"][i])
            values.append(result["Variable_Value"][i])
            if (str(result["Variable_Data_Type"][i][0][:3]) == 'ua.'):
                result["Variable_Data_Type"][i][0] = result["Variable_Data_Type"][i][0][3:]
            types.append(result["Variable_Data_Type"][i])
        if self.server != None:
            self.server.parameters.add_parameter(ExecutionParameter(service_uuid, task_uuid, values, names, types, name))

