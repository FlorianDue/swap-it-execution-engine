# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

from execution_engine_logic.data_types.types import EngineArray, EngineStruct

class DemoScenarioStructureTypes:

    def __init__(self):
        self.swap_order = None
        self.light_segment = None
        self.stand_segment = None
        self.raw_material = None
        self.blank = None
        self.resource_assignment = None
        self.capabilities = None
        self.assignment_agent = None
        self.registry = None
        self.create_type_descriptions()
        self.structures = [self.swap_order,
                           self.light_segment,
                           self.stand_segment,
                           self.raw_material,
                           self.blank,
                           self.resource_assignment,
                           self.capabilities,
                           self.assignment_agent,
                           self.registry]

    def create_type_descriptions(self):
        self.blank = EngineStruct("Blank")
        self.blank.set_struct_type("Blank")
        self.blank.add_attribute("blank_type", "string")
        self.blank.add_attribute("blank_id", "string")
        self.blank.add_attribute("part_id", "number")

        self.raw_material = EngineStruct("Raw_Material")
        self.raw_material.set_struct_type("Raw_Material")
        blank_array = EngineArray("blanks", 2)
        blank_array.data_type = "Blank"
        blank_array.values = []
        self.raw_material.add_attribute("blanks", blank_array)
        self.raw_material.add_attribute("blank_number", "number")

        self.light_segment = EngineStruct("Light_Segment")
        self.light_segment.set_struct_type("Light_Segment")
        self.light_segment.add_attribute("color", "string")
        self.light_segment.add_attribute("diameter", "number")
        self.light_segment.add_attribute("segment_id", "string")

        self.stand_segment = EngineStruct("Stand_Segment")
        self.stand_segment.set_struct_type("Stand_Segment")
        self.stand_segment.add_attribute("stand_shape", "string")
        self.stand_segment.add_attribute("stand_height", "number")
        self.stand_segment.add_attribute("stand_id", "string")

        self.swap_order = EngineStruct("SWAP_Order")
        self.swap_order.set_struct_type("SWAP_Order")
        self.swap_order.add_attribute("order_id", "number")
        self.swap_order.add_attribute("stand", "Stand_Segment")
        segments = EngineArray("segments", -1)
        segments.set_array_type("Light_Segment")
        segments.add_value([])
        self.swap_order.add_attribute("segments", segments)
        self.swap_order.add_attribute("number_light_segments", "number")

        self.resource_assignment = EngineStruct("ResourceAssignment")
        self.resource_assignment.set_struct_type("ResourceAssignment")
        self.resource_assignment.add_attribute("job_resource", "string")

        self.capabilities = EngineStruct("Milling_Capabilities")
        self.capabilities.set_struct_type("Milling_Capabilities")
        self.capabilities.add_attribute("test_numeric", "number")

        self.assignment_agent = EngineStruct("AssignmentAgent")
        self.assignment_agent.set_struct_type("AssignmentAgent")
        self.assignment_agent.add_attribute("agent", "string")

        self.registry = EngineStruct("DeviceRegistry")
        self.registry.set_struct_type("DeviceRegistry")
        self.registry.add_attribute("registry", "string")


class DemoScenarioStructureValues:

    def __init__(self):
        self.swap_order = None
        self.light_segment_1 = None
        self.light_segment_2 = None
        self.stand_segment = None
        self.raw_material = None
        self.blank = None
        self.resource_assignment = None
        self.assignment_agent = None
        self.registry = None
        self.create_type_values()

    def create_type_values(self):
        self.blank = EngineStruct("Blank")
        self.blank.set_struct_type("Blank")
        self.blank.add_attribute("blank_type", "test")
        self.blank.add_attribute("blank_id", "test")
        self.blank.add_attribute("part_id", 123)

        self.light_segment_1 = EngineStruct("Light_Segment")
        self.light_segment_1.set_struct_type("Light_Segment")
        self.light_segment_1.add_attribute("color", "red")
        self.light_segment_1.add_attribute("diameter", 5)
        self.light_segment_1.add_attribute("segment_id", "Default")

        self.stand_segment = EngineStruct("Stand_Segment")
        self.stand_segment.set_struct_type("Stand_Segment")
        self.stand_segment.add_attribute("stand_shape", "plate")
        self.stand_segment.add_attribute("stand_height", 3)
        self.stand_segment.add_attribute("stand_id", "Default")

        self.raw_material = EngineStruct("Raw_Material")
        self.raw_material.set_struct_type("Raw_Material")
        blank_array = EngineArray("blanks", 2)

        blank_1 = EngineStruct("Blank")
        blank_1.set_struct_type("Blank")
        blank_1.add_attribute("blank_type", "test")
        blank_1.add_attribute("blank_id", "test")
        blank_1.add_attribute("part_id", 123)

        blank_2 = EngineStruct("Blank")
        blank_2.set_struct_type("Blank")
        blank_2.add_attribute("blank_type", "test")
        blank_2.add_attribute("blank_id", "test")
        blank_2.add_attribute("part_id", 123)

        blank_array.data_type = "Blank"
        blank_array.values = [blank_1, blank_2]
        self.raw_material.add_attribute("blanks", blank_array)
        self.raw_material.add_attribute("blank_number", 2)

        self.swap_order = EngineStruct("SWAP_Order")
        self.swap_order.set_struct_type("SWAP_Order")
        self.swap_order.add_attribute("order_id", 1000)
        self.swap_order.add_attribute("stand", self.stand_segment)
        segments = EngineArray("segments", -1)
        segments.set_array_type("Light_Segment")
        self.light_segment_2 = EngineStruct("Light_Segment")
        self.light_segment_2.set_struct_type("Light_Segment")
        self.light_segment_2.add_attribute("color", "green")
        self.light_segment_2.add_attribute("diameter", 5)
        self.light_segment_2.add_attribute("segment_id", "Default")
        segments.add_value(self.light_segment_1)
        segments.add_value(self.light_segment_2)
        self.swap_order.add_attribute("segments", segments)
        self.swap_order.add_attribute("number_light_segments", 5)

        self.resource_assignment = EngineStruct("ResourceAssignment")
        self.resource_assignment.set_struct_type("ResourceAssignment")
        self.resource_assignment.add_attribute("job_resource", "opc.tcp://service_server:4081")

        self.capabilities = EngineStruct("Milling_Capabilities")
        self.capabilities.set_struct_type("Milling_Capabilities")
        self.capabilities.add_attribute("test_numeric", 5)

        self.assignment_agent = EngineStruct("AssignmentAgent")
        self.assignment_agent.set_struct_type("AssignmentAgent")
        self.assignment_agent.add_attribute("agent", "opc.tcp://assignment_agent:10000")

        self.registry = EngineStruct("DeviceRegistry")
        self.registry.set_struct_type("DeviceRegistry")
        self.registry.add_attribute("registry", "opc.tcp://device_registry:8000")



class DemoScenarioOPCUATypeInfo:
    def __init__(self):
        self.swap_order = []
        self.light_segment = []
        self.stand_segment = []
        self.raw_material = []
        self.blank = []
        self.resource_assignment = []
        self.capabilities = []
        self.assignment_agent = []
        self.registry = []
        self.create_type_descriptions()

    def create_type_descriptions(self):
        #blanks
        self.blank.append(FieldDescription("String", None, "blank_type"))
        self.blank.append(FieldDescription("String", None, "blank_id"))
        self.blank.append(FieldDescription("Double", None, "part_id"))
        #raw_material
        self.raw_material.append(FieldDescription("Blank", [1], "blanks"))
        self.raw_material.append(FieldDescription("Double", None, "blank_number"))
        #light_segment
        self.light_segment.append(FieldDescription("String", None, "color"))
        self.light_segment.append(FieldDescription("Double", None, "diameter"))
        self.light_segment.append(FieldDescription("String", None, "segment_id"))
        #stand_segment
        self.stand_segment.append(FieldDescription("String", None, "stand_shape"))
        self.stand_segment.append(FieldDescription("Double", None, "stand_height"))
        self.stand_segment.append(FieldDescription("String", None, "stand_id"))
        #swap_order
        self.swap_order.append(FieldDescription("String", None, "order_id"))
        self.swap_order.append(FieldDescription("Stand_Segment", None, "stand"))
        self.swap_order.append(FieldDescription("Light_Segment", [1], "segments"))
        self.swap_order.append(FieldDescription("Double", None, "number_light_segments"))

        self.resource_assignment.append(FieldDescription("String", None, "job_resource"))
        self.assignment_agent.append(FieldDescription("String", None, "agent"))
        self.registry.append(FieldDescription("String", None, "registry"))

        self.capabilities.append(FieldDescription("Double", None, "test_numeric"))

    def get_type_infor(self, req_type):
        if req_type == "SWAP_Order":
            return self.swap_order
        elif req_type == "Light_Segment":
            return self.light_segment
        elif req_type == "Stand_Segment":
            return self.stand_segment
        elif req_type == "Raw_Material":
            return self.raw_material
        elif req_type == "Blank":
            return self.blank
        elif req_type == "ResourceAssignment":
            return self.resource_assignment
        elif req_type == "Capabilities":
            return self.capabilities
        elif req_type == "AssignmentAgent":
            return self.assignment_agent
        elif req_type == "DeviceRegistry":
            return self.registry
class FieldDescription:
    def __init__(self, dataType, arrayDim, name):
        self.dataType = dataType
        self.arrayDim = arrayDim
        self.name = name

class AssignmentStructures:
    def __init__(self, custom_types, assignment_structure, assign_kwargs, capability_structure, capa_kwargs):
        self.assignment_structure_opcua = None
        self.capability_structure_opcua = None
        self.create_structures(custom_types, assignment_structure, assign_kwargs, capability_structure, capa_kwargs)
        self.resource_assignment = None
        self.capabilities = None

    def create_structures(self, custom_types, assignment_structure, assign_kwargs, capability_structure, capa_kwargs):
        for i in range(len(custom_types["Name"])):
            if custom_types["Name"][i] == assignment_structure:
                self.assignment_structure_opcua = custom_types["Class"][i](assign_kwargs)
            if custom_types["Name"][i] == capability_structure:
                self.assignment_structure_opcua = custom_types["Class"][i](capa_kwargs)

    def engine_structure_description(self):
        self.resource_assignment = EngineStruct("ResourceAssignment")
        self.resource_assignment.set_struct_type("ResourceAssignment")
        self.resource_assignment.add_attribute("job_resource", "opc.tcp://service_server:4081")

        self.capabilities = EngineStruct("Milling_Capabilities")
        self.capabilities.set_struct_type("Milling_Capabilities")
        self.capabilities.add_attribute("test_numeric", 5)
        self.capabilities.add_attribute("test_boolean", False)