# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

import asyncio
from datetime import datetime
from asyncua import ua
from execution_engine_logic.data_types.internal_data_converter import EngineOpcUaDataConverter
from execution_engine_logic.execution_engine_server import ExecutionEngineServer
from execution_engine_logic.data_object.data_object_interaction import DataObject
from control_interface.control_interface_highlevel import ControlInterface
from control_interface.target_server.target_server_dict import TargetServerList

class ExecutionEngine:

    def __init__(self, server_url, dispatcher_object, iteration_time = 0.001, log_info = False, number_default_clients = 1, device_registry_url = None, assignment_agent_url = None,
                 delay_start = None, custom_url = None):
        self.log_info = log_info if log_info else False
        self.server_url = server_url
        self.iteration_time = iteration_time if iteration_time is not None else 0.001
        self.server = None
        self.server_instance = None
        self.number_default_clients = number_default_clients if number_default_clients else 1
        self.device_registry_url = device_registry_url if device_registry_url else None
        self.assignment_agent_url = assignment_agent_url if assignment_agent_url else None
        self.delay_start = delay_start if delay_start else None
        self.dispatcher = dispatcher_object
        self.custom_url = custom_url if custom_url else None
        self.process = None

    async def start_server(self, struct_object, data_object):
        self.server = ExecutionEngineServer(self.server_url, self.iteration_time, self.log_info)
        self.server_instance = await self.server.start_server(struct_object, data_object)
        print("[", datetime.now(), "] Start Execution Engine ", self.server_instance)

    async def main(self):
        if self.delay_start != None:
            await asyncio.sleep(self.delay_start)
        await self.start_server(self.dispatcher.structs, DataObject(EngineOpcUaDataConverter()))
        self.dispatcher.set_callbacks(self.server_instance, self.server)
        ClientControlInterface = ControlInterface(self.server, self.server_instance, self.dispatcher.dispatcher_callbacks.service_execution_list,
                                                  TargetServerList(self.server, self.iteration_time, self.dispatcher.timeout), self.device_registry_url, self.assignment_agent_url, self.custom_url,
                                                  self.iteration_time, self.log_info, self.dispatcher.timeout)
        ClientControlInterface.init_default_clients(int(self.number_default_clients))
        self.dispatcher.dispatcher_callbacks.add_control_interface(ClientControlInterface)
        self.dispatcher.start_dispatcher()
        async with self.server_instance:
            while self.dispatcher.run_dispatcher():
                service_uuid, task_uuid, name = self.dispatcher.dispatcher_callbacks.service_execution_list.remove_service()
                if service_uuid != None:
                    await self.server.data_object.write_state_variable(task_uuid, ua.Variant(self.server.service_execution_states[0]))
                    if self.log_info:
                        print("[", datetime.now(), "] ---------> Set Token for Service ", name, " with uuid ", service_uuid)
                    self.dispatcher.fire_event(service_uuid)
                await asyncio.sleep(self.iteration_time)
            print("[", datetime.now(), "] Shut down the ControlInterface")
            for i in range(len(ClientControlInterface.client_dict["Client"])):
                ClientControlInterface.client_dict["Client"][i].stop_control_interface_loop()
            print("[", datetime.now(), "] Shut down the Execution Engine ", self.server_instance)
            #while True:
            #    await asyncio.sleep(1)
            await self.server.stop_server()
            print("[", datetime.now(), "] Execution Engine Completed the Process Execution")




