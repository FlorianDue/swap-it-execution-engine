# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
from control_interface.clients.event_subscription import ServiceEvents, SubHandler
from control_interface.clients.queue_interaction import TargetServerQueue
from control_interface.execute_service.interprete_result import ServiceResults
from control_interface.execute_service.assign_agent import AssignAgent
from asyncua import Client, ua
from datetime import datetime
import asyncio

class ExecutionClient:

    def __init__(self, running, server, service_execution_list, queue, target_server_list, iteration_time, log_info, custom_server_types):
        self.queue = queue
        self.custom_server_types = custom_server_types
        self.running = running
        self.server = server
        self.service_execution_list = service_execution_list
        self.target_server_list = target_server_list
        self.client_identifier = None
        self.service_res = None
        self.connected = False
        self.service_browse_name = None
        self.tar_server_url = None
        self.inp_args = None
        self.task_uuid = None
        self.service_uuid = None
        self.out_var = None
        self.device_registry_url = None
        self.assignment_agent_url = None
        self.docker = None
        self.iteration_time = iteration_time
        self.log_info = log_info
        self.timeout = None
        self.service_execution_states = [
            "ReadyForExecution",
            "ExecutionInProgess",
            "ExecutionCompleted"
        ]

    async def initiate_service_execution(self, service_browse_name, tar_server_url, inp_args, task_uuid, service_uuid, out_var, device_registry_url, assignment_agent_url):
        await self.server.data_object.write_state_variable(task_uuid, self.service_execution_states[1])
        if(tar_server_url == "None"):
            tar_server_url = await AssignAgent(self.docker, self.timeout).allocate_job_to_agent(service_browse_name, inp_args, device_registry_url, assignment_agent_url, self.custom_server_types)
        if(tar_server_url == None):
            while(tar_server_url == None):
                tar_server_url = await AssignAgent(self.docker, self.timeout).allocate_job_to_agent(service_browse_name, inp_args, device_registry_url, assignment_agent_url, self.custom_server_types)
                await asyncio.sleep(0.05)
        await self.execute_service(tar_server_url, service_browse_name, service_uuid, task_uuid, out_var, inp_args)
        await self.server.data_object.write_state_variable(task_uuid, self.service_execution_states[2])
        self.service_res.transmit_service_execution_finished(service_uuid, task_uuid, self.service_execution_list)

    async def execute_service(self, tar_server_url, service_browse_name, service_uuid, task_uuid, dlo_service_output, dlo_service_input):
        if self.log_info:
            print("[", datetime.now(), "] client connects to server: ", tar_server_url, " to execute service ", service_browse_name)
        async with Client(url=tar_server_url, timeout = self.timeout) as client:
            target_server = await self.target_server_list.get_target_server(tar_server_url, service_browse_name)
            queue = TargetServerQueue(self.iteration_time, client)
            service_parameter = await target_server.match_service_input(dlo_service_input, client, self.custom_server_types, service_browse_name)
            self.client_identifier = await queue.client_add_queue_element(target_server, service_uuid)
            await queue.wait_for_queue_position_one(target_server, self.client_identifier, service_uuid)
            await target_server.client_read_state_variable(client)
            handler = SubHandler(client, tar_server_url, self.log_info)
            self.service_res = ServiceResults()
            if target_server.implementation == 'open62541':
                service_parameter = await self.service_res.create_input_variant(service_parameter)
            if self.log_info:
                print("[", datetime.now(), "] Call Service Method with ", client, " with uuid ", self.client_identifier)
            await self.service_res.get_service_results(target_server, service_browse_name, service_parameter, handler, client, self.target_server_list, ServiceEvents(client, self.iteration_time, handler, target_server.event_node))
            if self.log_info:
                print("[", datetime.now(), "] The Service Results of ", client, " with uuid ", self.client_identifier, "are", self.service_res.result)
            await queue.client_remove_queue_element(target_server, service_uuid, self.client_identifier)
            await self.service_res.add_result_to_the_data_lifecycle_object(target_server, dlo_service_output, task_uuid, service_uuid, target_server.client_custom_data_types, service_browse_name)
            await client.get_node(target_server.state_variable).write_value(4, ua.VariantType.Int32)
            await client.disconnect()

    def stop_control_interface_loop(self):
        self.running = False

    def start_new_control_interface_loop(self):
        control_interface_loop = asyncio.new_event_loop()
        control_interface_loop.run_until_complete(self.start_client_loop())

    async def start_client_loop(self):
        while(self.running):
            if self.connected == False:
                inp = self.queue.get()
                if inp != None:
                    self.get_input_values(inp)
                await asyncio.sleep(self.iteration_time)
            else:
                await self.initiate_service_execution(self.service_browse_name, self.tar_server_url, self.inp_args, self.task_uuid, self.service_uuid, self.out_var, self.device_registry_url, self.assignment_agent_url)
                self.reset_connection()

    def get_input_values(self, inp):
        self.service_browse_name = inp[0]
        self.tar_server_url = inp[1]
        self.inp_args = inp[2]
        self.task_uuid = inp[3]
        self.service_uuid = inp[4]
        self.out_var = inp[5]
        self.device_registry_url = inp[6]
        self.assignment_agent_url = inp[7]
        self.docker = inp[8]
        self.timeout = inp[9]
        self.connected = True

    def reset_connection(self):
        self.service_browse_name = None
        self.tar_server_url = None
        self.inp_args = None
        self.task_uuid = None
        self.service_uuid = None
        self.out_var = None
        self.connected = False
        self.device_registry_url = None
        self.assignment_agent_url = None
        self.docker = None

