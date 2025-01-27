# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
import uuid
from asyncua import ua
from asyncua.common.instantiate_util import instantiate
from execution_engine_logic.data_object.object_types import ObjectTypes

class InstantiateTypes:

    def __init__(self, server, idx):
        self.server = server
        self.idx = idx
        self.types = ObjectTypes(self.server, self.idx)
        self.path_to_custom_structs = ["0:Types", "0:DataTypes", "0:BaseDataType", "0:Structure"]
        self.custom_data_types = {"Name": [], "Class": [], "NodeId": []}
        self.life_cycle_name = "LifeCycleObject"
        self.task_node = None
        self.service_started_event = None
        self.service_finished_event = None


    async def load_custom_data_types(self):
        custom_type_definitions = await self.server.load_data_type_definitions()
        for name, obj in custom_type_definitions.items():
            self.custom_data_types["Name"].append(name)
            self.custom_data_types["Class"].append(obj)
            self.custom_data_types["NodeId"].append(await self.server.nodes.root.get_child(
                [*self.path_to_custom_structs,
                 str(self.idx) + ":" + str(name)]))
        return self.custom_data_types

    async def instantiate_data_object(self, service_started, service_finished, task_started, task_finished):
        self.data_lifecycle_object_type = await self.types.create_lifecycle_object_type()
        await instantiate(self.server.nodes.objects, self.data_lifecycle_object_type, bname=str(self.idx) + ":" + str(self.life_cycle_name))
        self.service_started_event = service_started
        self.service_finished_event = service_finished
        self.task_finished_event = task_finished
        self.task_started_event = task_started

    async def instantiate_task_object(self, task_uuid, task_name, task_context_uuid):
        task_object = await self.types.taks_object_type(task_name)
        node_id = ua.NodeId(Identifier=uuid.UUID(task_uuid), NamespaceIndex=self.idx, NodeIdType=ua.NodeIdType.Guid)
        if str(task_uuid) == str(task_context_uuid):
            data_lifcycle_object = await self.server.nodes.objects.get_child([str(self.idx)+ ":" + self.life_cycle_name])
            await data_lifcycle_object.add_object(node_id, "2:"+task_uuid, task_object.nodeid)
        else:
            prod_task = self.server.get_node(ua.NodeId(Identifier=uuid.UUID(task_context_uuid), NamespaceIndex=self.idx, NodeIdType=ua.NodeIdType.Guid))
            await prod_task.add_object(node_id, "2:"+task_uuid, task_object.nodeid)