# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

from asyncua import Server
from execution_engine_logic.service_execution.execution_results import ExecutionParameterList
from execution_engine_logic.data_types.opcua_type_generator import TypeGenerator

class ExecutionEngineServer:

    def __init__(self, execution_engine_server_url, iteration_time, log_info):
        self.server_url = execution_engine_server_url
        self.log_info = log_info
        self.iteration_time = iteration_time
        self.server = None
        self.idx = None
        self.ee_namespace_idx = None
        self.data_object = None
        self.custom_data_types = None
        self.parameters = ExecutionParameterList()
        self.service_execution_states = [
            "ReadyForExecution",
            "ExecutionInProgess",
            "ExecutionCompleted"
        ]

    async def init_server(self):
        self.server = Server()
        await self.server.init()
        self.server.set_server_name("Execution Engine")
        self.server.set_endpoint(self.server_url)
        self.idx = await self.server.register_namespace("http://exection_engine.fraunhofer.iosb.de")
        self.data_object = None

    async def start_server(self, struct_object, data_object):
        await self.init_server()
        self.data_object = data_object
        self.data_object.set_idx(self.idx)
        self.data_object.set_server(self.server)
        await self.server.import_xml("model/SWAP.Fraunhofer.Execution.Engine.Model.NodeSet2.xml")
        namespaces = await self.server.get_namespace_array()
        for i in range(len(namespaces)):
            if str(namespaces[i]) == "http://execution.engine.swap.fraunhofer.de":
                self.ee_namespace_idx = i
                break
        service_started = await self.server.nodes.root.get_child(
            ["0:Types", "0:EventTypes", "0:BaseEventType", str(self.ee_namespace_idx)+":ServiceStartedEvent"])
        service_finished = await self.server.nodes.root.get_child(
            ["0:Types", "0:EventTypes", "0:BaseEventType", str(self.ee_namespace_idx)+":ServiceFinishedEvent"])
        task_started = await self.server.nodes.root.get_child(
            ["0:Types", "0:EventTypes", "0:BaseEventType", str(self.ee_namespace_idx)+":TaskStartedEvent"])
        task_finished = await self.server.nodes.root.get_child(
            ["0:Types", "0:EventTypes", "0:BaseEventType", str(self.ee_namespace_idx)+":TaskFinishedEvent"])
        #todo use running variable fro dispatcher
        await TypeGenerator(self).create_opcua_types(struct_object)
        self.custom_data_types = await self.data_object.opcua_declarations.load_custom_data_types()
        await self.data_object.opcua_declarations.instantiate_data_object(service_started, service_finished, task_started, task_finished)
        return self.server

    async def stop_server(self):
        await self.server.stop()



