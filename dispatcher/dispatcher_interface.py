# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
from dispatcher.dispatcher_callbacks.cb_functions import DispatcherCallbackFunctions
from execution_engine_logic.data_types.internal_data_converter import EngineOpcUaDataConverter, OpcUaEngineDataConverter
from execution_engine_logic.data_types.types import EngineStruct
import asyncio, nest_asyncio

class DispatcherInterface:

    def __init__(self):
        self.dispatcher = None
        self.structs = None
        self.dispatcher_callbacks = None
        self.server = None
        self.ee_opc_ua_converter = EngineOpcUaDataConverter()
        self.opc_ua_ee_converter = OpcUaEngineDataConverter()
        self.callback_loop = asyncio.new_event_loop()
        nest_asyncio.apply(self.callback_loop)
        self.fire_event = None
        self.task_started_interface = None
        self.task_finished_interface = None
        self.service_finished_interface = None
        self.service_started_interface = None
        self.data_provider_interface = None
        self.register_dispatcher_callbacks = None
        self.start_dispatcher = None
        self.running = None

    def set_dispatcher(self, dispatcher):
        self.dispatcher = dispatcher

    def set_register_dispatcher_callbacks(self, func):
        self.register_dispatcher_callbacks = func

    def set_callbacks(self, server_instance, server):
        self.dispatcher_callbacks = DispatcherCallbackFunctions(server_instance, server, server.data_object, self.ee_opc_ua_converter, self.opc_ua_ee_converter)
        self.register_dispatcher_callbacks()
        self.server = server

    def set_process_parameter(self, structs):
        self.structs = structs

    def set_interfaces(self, task_started, task_finished, service_finished, service_started, data_provider):
        self.task_started_interface = task_started
        self.task_finished_interface = task_finished
        self.service_finished_interface = service_finished
        self.service_started_interface = service_started
        self.data_provider_interface = data_provider

    def set_fire_event_method(self, fire_event_method):
        self.fire_event = fire_event_method

    def set_start_dispatcher(self, func):
        self.start_dispatcher = func

    def set_running(self, func):
        self.running = func

    def start_dispatcher(self):
        self.start_dispatcher()

    def run_dispatcher(self):
        return self.running(self.dispatcher)


    def task_finished_callback_wrapper(self, name, uuid, task_context_uuid, output_parameter):
        self.callback_loop.run_until_complete(self.dispatcher_callbacks.task_finished_cb(name, uuid, task_context_uuid, output_parameter))

    def task_started_callback_wrapper(self, task_name, task_uuid, task_context_uuid, task_input_parameter_names, task_input_parameter_instances):
        self.callback_loop.run_until_complete(self.dispatcher_callbacks.task_started_cb(task_name, task_uuid, task_context_uuid, task_input_parameter_names, task_input_parameter_instances))

    def service_finished_callback_wrapper(self, name, task_context_uuid, service_uuid):
        self.callback_loop.run_until_complete(self.dispatcher_callbacks.service_finished_cb(name, task_context_uuid, service_uuid))

    def service_started_callback_wrapper(self, name, service_uuid, task_context_uuid, input_parameters, output_parameters):
        input_parameters = self.map_input_parameters_to_opcua(input_parameters)
        self.callback_loop.run_until_complete(self.dispatcher_callbacks.service_started_cb(name, service_uuid, task_context_uuid, input_parameters , output_parameters))

    def provide_parameter_wrapper(self, variable_name, task_id):
        return variable_name, self.callback_loop.run_until_complete(self.dispatcher_callbacks.provide_parameter(variable_name, task_id))

    def map_input_parameters_to_opcua(self, input_parameter_values):
        input_parameters = []
        if len(input_parameter_values) > 0:
            for i in range(len(input_parameter_values)):
                if isinstance(input_parameter_values[i], EngineStruct):
                    input_parameters.append(self.ee_opc_ua_converter.create_opcua_format(self.server, input_parameter_values[i]))
                else:
                    input_parameters.append(input_parameter_values[i])
        return input_parameters




