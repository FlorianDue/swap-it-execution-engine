# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

from pfdl_scheduler.model.array import Array
from pfdl_scheduler.scheduler import Scheduler, Event
from pfdl_scheduler.api.task_api import TaskAPI
from pfdl_scheduler.api.service_api import ServiceAPI
from pfdl_scheduler.model.struct import Struct

from execution_engine_logic.data_types.types import EngineArray, EngineStruct
from dispatcher.dispatcher_interface import DispatcherInterface

class DispatcherConfig:

    def __init__(self, filepath, dashboard_host_address = None):
        self.dispatcher_object = DispatcherInterface()
        self.filepath = filepath
        self.dashboard_host_address = dashboard_host_address
        self.scheduler = Scheduler(self.filepath,dashboard_host_address=self.dashboard_host_address) if self.dashboard_host_address else Scheduler(self.filepath)
        self.structs = []
        self.config_dispatcher()

    def config_dispatcher(self):
        self.dispatcher_object.set_dispatcher(self.scheduler)
        for key,value in self.scheduler.process.structs.items():
            self.structs.append(PfdlEeDataconverter().create_ee_format(value))
        self.dispatcher_object.set_process_parameter(self.structs)
        self.dispatcher_object.set_start_dispatcher(self.dispatcher_object.dispatcher.start)
        self.dispatcher_object.set_running(self.return_running)
        self.dispatcher_object.set_register_dispatcher_callbacks(self.register_dispatcher_callbacks)
        self.dispatcher_object.set_fire_event_method(self.fire_dispatcher_event)


    def return_running(self, dispatcher):
        return dispatcher.running
    def register_dispatcher_callbacks(self):
        self.dispatcher_object.dispatcher.register_callback_service_started(self.service_started_interface)
        self.dispatcher_object.dispatcher.register_callback_service_finished(self.service_finished_interface)
        self.dispatcher_object.dispatcher.register_callback_task_started(self.task_started_interface)
        self.dispatcher_object.dispatcher.register_callback_task_finished(self.task_finished_interface)
        self.dispatcher_object.dispatcher.register_variable_access_function(self.data_provider_interface)

    def fire_dispatcher_event(self, service_uuid):
        self.scheduler.fire_event(Event(event_type="service_finished",
                                   data={"service_id": service_uuid}))

    def task_started_interface(self, task_api: TaskAPI):
        task_context_uuid = task_api.uuid if task_api.task.name == "productionTask" else task_api.task_context.uuid
        input_parameters = self.map_input_parameters_to_EE(task_api.input_parameters)
        self.dispatcher_object.task_started_callback_wrapper(task_api.task.name, task_api.uuid, task_context_uuid,
                                                        task_api.task.input_parameters, input_parameters)

    def task_finished_interface(self, task_api: TaskAPI):
        task_context_uuid = task_api.uuid if task_api.task.name == "productionTask" else task_api.task_context.uuid
        self.dispatcher_object.task_finished_callback_wrapper(task_api.task.name, task_api.uuid, task_context_uuid,
                                                         task_api.task.output_parameters)

    def service_finished_interface(self, service_api: ServiceAPI):
        self.dispatcher_object.service_finished_callback_wrapper(service_api.service.name,
                                                            service_api.uuid, service_api.task_context.uuid)

    def service_started_interface(self, service_api: ServiceAPI):
        input_parameters = self.map_input_parameters_to_EE(service_api.input_parameters)
        self.dispatcher_object.service_started_callback_wrapper(service_api.service.name, service_api.uuid, input_parameters,
                                                           service_api.service.output_parameters,
                                                           service_api.task_context.uuid)

    def data_provider_interface(self, variable_name, task_id):
        variable_name, struct = self.dispatcher_object.provide_parameter_wrapper(variable_name, task_id.uuid)
        return EePfdlConverter().convert_ee_to_pfdl(variable_name, struct)

    def map_input_parameters_to_EE(self, input_parameter_values):
        input_parameters = []
        if len(input_parameter_values) > 0:
            for i in range(len(input_parameter_values)):
                if isinstance(input_parameter_values[i], Struct):
                    input_parameters.append(PfdlEeDataconverter().create_ee_format(input_parameter_values[i]))
                else:
                    input_parameters.append(input_parameter_values[i])
        return input_parameters


class EePfdlConverter:

    def convert_ee_to_pfdl(self, variable_name, server_struct):
        variable = Struct()
        variable.name = variable_name
        if isinstance(server_struct, EngineStruct):
            for (name, value) in server_struct.attributes.items():
                if isinstance(value, str) or isinstance(value, bool) or isinstance(value, int) or isinstance(value, float):
                    variable.attributes[name] = value
                elif isinstance(value, EngineArray):
                    vals = Array()
                    vals.length = value.length
                    vals.name = name
                    for i in range(value.length):
                        vals.values.append(self.convert_ee_to_pfdl(name, value.values[i]))
                        variable.attributes[name] = vals
                else:
                    variable.attributes[name] = self.convert_ee_to_pfdl(name, value)
        return variable

class PfdlEeDataconverter:

    def create_ee_format(self, initial_type):
        item = EngineStruct(initial_type.name)
        item = self.convert_to_EE_struct(initial_type, item)
        item.set_struct_type(initial_type.name)
        return item

    def convert_array(self, array, item):
        for i in range(len(array.values)):
            if isinstance(array.values[i], Struct):
                val = EngineStruct(array.values[i].name)
                val = self.convert_to_EE_struct(array.values[i], val)
                val.set_struct_type(array.values[i].name)
                item.add_value(val)
            elif isinstance(array.values[i], Array):
                val = EngineArray(array.values[i].name, array.values[i].length)
                val.set_array_type(array.values[0].data_type)
                val = self.convert_array(array.values[i], val)
                item.add_value(val)
            else:
                item.add_value(array.values[i].values)
        return item

    def convert_to_EE_struct(self, struct, item):
        for(key, value) in struct.attributes.items():
            if isinstance(value, Struct):
                val = EngineStruct(key)
                val.set_struct_type(value.name)
                val = self.convert_to_EE_struct(value, val)
                item.add_attribute(key, val)
            elif isinstance(value, Array):
                val = EngineArray(key, value.length)
                val.set_array_type(value.type_of_elements)
                if val.data_type == '':
                    val.set_array_type(value.values[0].name)
                val = self.convert_array(value, val)
                item.add_attribute(key, val)
            else:
                item.add_attribute(key, value)
        return item
