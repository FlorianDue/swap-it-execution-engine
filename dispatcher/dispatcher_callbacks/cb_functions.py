# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
from dispatcher.dispatcher_callbacks.cb_util import CallbackHelpers
from dispatcher.dispatcher_callbacks.cb_events import CallbackEvents
from execution_engine_logic.service_execution.execution_dict import ServiceInfo, ExecutionList
from datetime import datetime
import uuid, asyncio
from asyncua import ua

class DispatcherCallbackFunctions:

    def __init__(self, server_instance: object, server: object, opcua_data_converter, ee_data_converter) -> object:
        self.server = server
        self.server_instance = server_instance
        self.service_execution_list = ExecutionList()
        self.callback_helpers = CallbackHelpers(self.server.data_object)
        self.target_server_list = None
        self.control_interface = None
        self.ee_data_converter = ee_data_converter
        self.opcua_data_converter = opcua_data_converter
        self.baseTaskuuid = None
        self.events = CallbackEvents(self.server, self.server_instance)

    def add_control_interface(self, ControlInterface):
        self.control_interface = ControlInterface
        self.target_server_list = self.control_interface.target_server_list

    async def task_finished_cb(self, name:str, task_identifier, context:str, output_parameters):
        await self.events.fire_task_finished_event(task_identifier, name)
        if self.server.log_info:
            print("[", datetime.now(), "] Task " + name +" with UUID: " + task_identifier + " finished in context ", context)
        if len(output_parameters) != 0 and context != task_identifier:
            for variable in output_parameters:
                if isinstance(variable, list):
                    val = await self.callback_helpers.browse_struct_fields(task_identifier, variable)
                    self.existing_val, self.node = await self.server.data_object.read_struct_values(context,
                                                                                                    variable[len(variable)-2] if (variable[len(variable)-1][0] == '[' and variable[len(variable)-1][len(variable[len(variable)-1])-1] == ']') else variable[len(variable)-1])
                    variable = variable[len(variable)-2]+variable[len(variable)-1] if (variable[len(variable)-1][0] == '[' and variable[len(variable)-1][len(variable[len(variable)-1])-1] == ']') else variable[len(variable)-1]
                else:
                    val, _ = await self.server.data_object.read_struct_values(task_identifier, str(variable))
                    self.existing_val, self.node = await self.server.data_object.read_struct_values(context, str(variable))
                if self.existing_val != None:
                    await self.server.data_object.remove_node(self.existing_val.data_type if hasattr(self.existing_val, 'data_type') else self.node)
                data_type = val.data_type if hasattr(val, 'data_type') else type(val).__name__
                if str(data_type) == 'int' or str(data_type) == 'float' or str(data_type) == 'double':
                    data_type = "number"
                elif str(data_type) == "str":
                    data_type = "string"
                elif str(data_type) == "bool":
                    data_type = "boolean"
                await self.server.data_object.add_struct_variable([variable], [data_type], [val],
                                                                  context, self.server_instance, self.server)
        if task_identifier != context:
            await self.server.data_object.remove_node(ua.NodeId(Identifier=uuid.UUID(task_identifier), NamespaceIndex=self.server.idx, NodeIdType=ua.NodeIdType.Guid))

    async def task_started_cb(self, name:str, task_identifier, context:str, input_parameters, parameters_instances):
        await self.events.fire_task_started_event(task_identifier, name)
        if self.server.log_info:
            print("[", datetime.now(), "] Task " + name +" with UUID: " + task_identifier + " started in context ", context)
        await self.server.data_object.opcua_declarations.instantiate_task_object(task_identifier, name, context)
        if task_identifier != context:
            variables = await self.callback_helpers.create_task_variables(parameters_instances, context, self.server, self.opcua_data_converter)
            await self.server.data_object.add_struct_variable(*self.callback_helpers.get_input_names_and_types(input_parameters), variables['Input_Value'], task_identifier, self.server_instance, self.server)
        else:
            self.baseTaskuuid = task_identifier

    async def service_started_cb(self, name, service_uuid, input_parameters, output_parameters, context = None):
        if self.baseTaskuuid == None and context == None:
            context = self.baseTaskuuid = str(uuid.uuid4())
            await self.server.data_object.opcua_declarations.instantiate_task_object(self.baseTaskuuid, "DefaultTask", self.baseTaskuuid)
        if self.server.log_info:
            print("[", datetime.now(), "] Service " + str(name) + " with UUID " + str(service_uuid) + " started in context " + str(context))
        await self.events.fire_service_started_event(service_uuid, name)

        self.service_execution_list.add_service(ServiceInfo(service_uuid, context, False, name))
        names, values = await self.callback_helpers.read_struct_value_from_data_object(*self.callback_helpers.classify_service_input(input_parameters), context)
        o_parameters = self.callback_helpers.read_service_output_parameter(output_parameters)
        tar_server_url = self.callback_helpers.check_for_target_type(self.server, values, "ResourceAssignment")
        assignment_agent_url = self.callback_helpers.check_for_target_type(self.server, values, "AssignmentAgent")
        device_registry_url = self.callback_helpers.check_for_target_type(self.server, values, "DeviceRegistry")
        self.control_interface.start_client_interaction(name, str(tar_server_url), [names, values], context, service_uuid, o_parameters, assignment_agent_url, device_registry_url)

    async def service_finished_cb(self, name, service_identifier, context = None):
        if context == None:
            context = self.baseTaskuuid
        if self.server.log_info:
            print("[", datetime.now(), "] Service " + name + " with UUID " + service_identifier + " finished  in context " + context)
        await self.events.fire_service_finished_event(service_identifier, name)
        for parameter in self.server.parameters.parameters:
            if str(parameter.context) == str(context) and str(parameter.service_uuid) == str(service_identifier):
                for variable in range(len(parameter.variables)):
                    val, _ = await self.server.data_object.read_struct_values(parameter.context, parameter.variables[variable])
                    if val != None:
                        await self.server.data_object.remove_node(self.server.data_object.get_nodeId_fromType(str(parameter.type[variable])))
                    await self.server.data_object.add_struct_variable([parameter.variables[variable]], [parameter.type[variable]], [parameter.results[variable]],
                                                                      parameter.context, self.server_instance, self.server)
                self.server.parameters.remove_parameter(parameter.service_uuid)

    async def read_struct_parameter_from_server(self, variable_name, task_id):
        val, _ = await self.server.data_object.read_struct_values(task_id, variable_name)
        return self.ee_data_converter.convert_opcua_to_ee(variable_name, val, self.server)

    async def provide_parameter(self, service_id, task_id):
        return await self.read_struct_parameter_from_server(service_id, task_id)
