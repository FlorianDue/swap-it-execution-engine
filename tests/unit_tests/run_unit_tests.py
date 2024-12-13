# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)
import sys, os, unittest
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../tests/test_helpers/."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../control_interface/."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../execution_engine_logic/."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../dispatcher/."))
from check_control_interface.run_unit_tests import RunControlInterfaceTests
from check_execution_engine_logic.run_unit_tests import RunExecutionEngineLogicTests
from check_dispatcher.run_unit_tests import RunDispatcherTests
from util.start_docker_compose import DockerComposeEnvironment



class ExecuteUnitTests(unittest.TestCase):

    def test_run_unit_tests(self):
        print("start tests")
        env = DockerComposeEnvironment(["Device_Registry", "Service_Server"])
        custom_type_definitions = RunExecutionEngineLogicTests().run_execution_engine_logic_tests(env = env)
        custom_type_definitions = RunControlInterfaceTests().run_control_interface_tests(custom_data_types=custom_type_definitions, env = env)
        custom_type_definitions = RunDispatcherTests().run_dispatcher_tests(custom_data_types = custom_type_definitions, env = env)
        env.stop_docker_compose()
        print("completed tests")


if __name__ == "__main__":
    unittest.main()
