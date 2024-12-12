# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

import asyncio, sys
from execution_engine_logic.execution_engine import ExecutionEngine
from dispatcher.dispatcher_configuration import DispatcherConfig


def main():
    optinal_arguments = dict(arg.split("=") for arg in sys.argv[3:])
    dispatcher_object = DispatcherConfig(filepath=sys.argv[2], dashboard_host_address=optinal_arguments[
        "dashboard_host_address"] if optinal_arguments.__contains__(
        "dashboard_host_address") else None).dispatcher_object
    if optinal_arguments.__contains__("dashboard_host_address"):
        optinal_arguments.__delitem__("dashboard_host_address")
    execute_process(sys.argv[1], dispatcher_object, **optinal_arguments)

def execute_process(server_url, dispatcher_object, log_info = False, device_registry_url = None, custom_url = None, number_default_clients = 1, assignment_agent_url = None, delay_start = None):

    main_loop = asyncio.new_event_loop()
    main_loop.run_until_complete(ExecutionEngine(
        server_url=server_url,
        dispatcher_object=dispatcher_object,
        log_info=log_info,
        device_registry_url=device_registry_url,
        custom_url=custom_url,
        number_default_clients=number_default_clients,
        assignment_agent_url= assignment_agent_url,
        delay_start=delay_start
    ).main())

if __name__ == "__main__":
    main()

