# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
from asyncua import ua
class ObjectTypes:

    def __init__(self, server, idx):
        self.server = server
        self.idx = idx
        self.state_variable = "StateVariable"
        self.current_execution = "CurrentExecution"
        self.data_object = "DataObject"
        self.task_object_type = "TaskObjectType"
        self.taskName = "TaskName"
        self.initial_state = "Initial"

    async def create_lifecycle_object_type(self):
        dlo = await self.server.nodes.base_object_type.add_object_type(self.idx, self.data_object)
        return dlo

    async def taks_object_type(self, task_name):
        self.task_name = task_name
        task_object_type = await self.server.nodes.base_object_type.add_object_type(self.idx, self.task_object_type)
        task = await task_object_type.add_property(self.idx, self.taskName, self.task_name)
        await task.set_modelling_rule(True)
        state_variable = await task_object_type.add_property(self.idx, self.state_variable, self.initial_state)
        await state_variable.set_writable()
        await state_variable.set_modelling_rule(True)
        current_execution = await task_object_type.add_property(self.idx, self.current_execution, "None")
        await current_execution.set_writable()
        await current_execution.set_modelling_rule(True)
        return task_object_type

