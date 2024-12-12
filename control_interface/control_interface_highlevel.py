# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
from control_interface.clients.execution_client import ExecutionClient
import threading
from queue import Queue

class ControlInterface:

    def __init__(self, server, server_instance, service_execution_list, target_server_list, device_registry_url, assignment_agent_url, docker, iteration_time, log_info, timeout):
        self.server = server
        self.server_instance = server_instance
        self.iteration_time = iteration_time
        self.log_info = log_info
        self.service_execution_list = service_execution_list
        self.target_server_list = target_server_list
        self.device_registry_url = device_registry_url
        self.assignment_agent_url = assignment_agent_url
        self.client_identifier = None
        self.service_res = None
        self.running = True
        self.docker = docker
        self.timeout = timeout
        self.client_dict = {"Client":[], "Queue":[], "Thread":[]}

    def start_client_interaction(self, service_browse_name, tar_server_url, inp_args, task_uuid, service_uuid,
               out_var, assignment_agent_url, device_registry_url):
        client_started = False
        for i in range(len(self.client_dict["Client"])):
            if(self.client_dict["Client"][i].connected == False):
                self.start_client_execution(self.client_dict["Queue"][i], service_browse_name, tar_server_url, inp_args, task_uuid, service_uuid,
               out_var, assignment_agent_url, device_registry_url)
                client_started = True
                break
        if client_started == False:
            queue = self.start_new_client()
            self.start_client_execution(queue, service_browse_name, tar_server_url, inp_args, task_uuid, service_uuid,
               out_var, assignment_agent_url, device_registry_url)

    def start_new_client(self):
        queue = Queue()
        client = ExecutionClient(self.running, self.server, self.service_execution_list, queue, self.target_server_list, self.iteration_time, self.log_info, self.server.custom_data_types)
        client_thread = threading.Thread(target = client.start_new_control_interface_loop, daemon=True)
        self.client_dict["Client"].append(client)
        self.client_dict["Queue"].append(queue)
        self.client_dict["Thread"].append(client_thread)
        client_thread.start()
        return queue

    def start_client_execution(self, queue, service_browse_name, tar_server_url, inp_args, task_uuid, service_uuid,
               out_var, assignment_agent, device_registry):
        inp = [service_browse_name,
               tar_server_url,
               inp_args,
               task_uuid,
               service_uuid,
               out_var,
               self.device_registry_url if device_registry == None else device_registry,
               self.assignment_agent_url if assignment_agent == None else assignment_agent,
               self.docker,
               self.timeout]
        queue.put(inp)

    def init_default_clients(self, number_of_clients):
        for i in range(number_of_clients):
            self.start_new_client()
