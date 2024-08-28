import unittest, asyncio
from tests.test_helpers.values.ee_structures import DemoScenarioStructureValues, DemoScenarioStructureTypes
from execution_engine_logic.data_types.internal_data_converter import EngineOpcUaDataConverter, OpcUaEngineDataConverter
from execution_engine_logic.execution_engine_server import ExecutionEngineServer
from execution_engine_logic.data_object.data_object_interaction import DataObject
from execution_engine_logic.data_types.types import EngineArray, EngineStruct
from asyncua import Client

class CheckInternalDataConverter(unittest.TestCase):

    async def check_internal_data_transformer(self, cov, custom_type_definitions):
        cov.start()
        iteration_time = 0.001
        server_url = "opc.tcp://localhost:4002"
        server_instance = ExecutionEngineServer(execution_engine_server_url=server_url, log_info=True,
                                                iteration_time=iteration_time)
        await server_instance.init_server()
        types = DemoScenarioStructureTypes()
        structures = [types.swap_order, types.light_segment, types.stand_segment, types.raw_material, types.blank]
        server = await server_instance.start_server(structures, DataObject(EngineOpcUaDataConverter()))
        opcua_converter = EngineOpcUaDataConverter()
        ee_converter = OpcUaEngineDataConverter()
        structure_values = DemoScenarioStructureValues()
        generated_opcua_values, generated_ee_struct_values = [], []
        async with server:
            # convert all structures to opcua values
            for name, obj in structure_values.__dict__.items():
                print(custom_type_definitions)
                value = opcua_converter.convert_to_opcua_struct(obj, custom_type_definitions, obj.data_type)
                generated_opcua_values.append(value)
                self.check_generated_opcua(value, obj)
            # convert the generated opc ua values back to engine values
            print(generated_opcua_values)
            ctr = 0
            for name, obj in structure_values.__dict__.items():
                value = ee_converter.convert_opcua_to_ee(str(type(generated_opcua_values[ctr]).__name__), generated_opcua_values[ctr], server_instance)
                generated_ee_struct_values.append(value)
                self.check_generated_engine_types(obj, value)
                ctr += 1
            await server_instance.stop_server()
        cov.stop()


    def check_generated_engine_types(self, obj, ee_struct):
        #self.assertEqual(obj.data_type, ee_struct.data_type)
        for name, obj in obj.attributes.items():
            if isinstance(obj, EngineStruct):
                self.check_generated_engine_types(obj, ee_struct.attributes[name])
            elif isinstance(obj, EngineArray):
                self.assertEqual(obj.name, ee_struct.attributes[name].name)
                for i in range(len(obj.values)):
                    self.check_generated_engine_types(obj.values[i], ee_struct.attributes[name].values[i])
            else:
                self.assertEqual(obj, ee_struct.attributes[name])

    def check_generated_opcua(self, obj, ee_struct):
        for name, obj in obj.__dict__.items():
            if isinstance(ee_struct.attributes[name], EngineStruct):
                self.check_generated_opcua(obj, ee_struct.attributes[name])
            elif isinstance(ee_struct.attributes[name], EngineArray):
                for i in range(ee_struct.attributes[name].length):
                    self.check_generated_opcua(obj[i], ee_struct.attributes[name].values[i])
            else:
                self.assertEqual(obj, ee_struct.attributes[name])

    def check_start_simple_server(self, cov, custom_type_definitions):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.check_internal_data_transformer(cov, custom_type_definitions))
