..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)





============================
Capability-based Assignment
============================


The `Demonstration Scenario <https://github.com/swap-it/demo-scenario>`_ defines a structure SWAP_Order that must be handed over to each service to be executed.
For the Capability-based Assignment, a Device Registry is required, which interprets restrictions defined by capabilities.
Besides, the default assignment strategy is applied.

To consider Capabilities a service specific Capability structure must be defined, in this case a *Coating_Capability* to restrict the assignment of the Coating service. Within the demonstration scenario shop floor,
3 Coating resources are available, where each of them provides a *test_numeric* and a *test_boolean* capability. For example, the resources defines the comparative operator for the *test_boolean* capability as IsFalse,
so that restrictions, provided by the Coating_Capabilities where the *test_boolean* field is false, will restrict the selection to the resource which has the capability defined as false.


PFDL Definition
================


.. code-block:: python

    Struct SWAP_Order
        order_id:number
        stand:Stand_Segment
        segments: Light_Segment[]
        number_light_segments: number
    End

    Struct Stand_Segment
                stand_shape:string
                stand_height:number
                stand_id:string
    End

    Struct Light_Segment
                color: string
                diameter: number
                segment_id:string
    End

    Struct Coating_Capabilities
            test_numeric:number
            test_boolean:bool
    End

    Task productionTask
                manufacture_light_segments
                    In
                        SWAP_Order
                        {
                            "order_id":1000,
                            "stand":{
                                "stand_shape":"plate",
                                "stand_height":3,
                                "stand_id": "Default"
                            },
                            "segments":
                            [
                            {
                                "color": "red",
                                "diameter": 5,
                                "segment_id": "Default"
                            },
                            {
                                "color": "green",
                                "diameter": 5,
                                "segment_id": "Default"
                            }
                            ],
                            "number_light_segments": 5
                        }
    End

    Task manufacture_light_segments
                In
                    order: SWAP_Order
                Parallel Loop i To order.number_light_segments
                    manufacture_light_segment
                        In
                            order
                        Out
                            order:SWAP_Order
                Loop i To order.number_light_segments
                    Gluing
                        In
                            order
                        Out
                            order:SWAP_Order
    End

    Task manufacture_light_segment
                In
                    order: SWAP_Order
                GetPartsFromWarehouse
                    In
                        order
                    Out
                        order: SWAP_Order
                Coating
                    In
                        order
                        #we restrict the resources to the one that defines the
                        #test_boolean value
                        Coating_Capabilities
                        {
                            "test_boolean":True,
                            "test_numeric":90
                        }
                    Out
                        order: SWAP_Order
                Out
                    order
    End



Process Execution
=================
To execute the above-defined PFDL-process, a small `python script <https://github.com/FraunhoferIOSB/swap-it-execution-engine/blob/main/Tutorial/capability_based_assignment.py>`_
is required to set up the execution engine and the docker environment:

.. code-block:: python

    import time, os, sys
    #add directories to the system path
    sys.path.append(os.path.join(os.path.dirname(__file__), "../."))
    sys.path.append(os.path.join(os.path.dirname(__file__), "../tests/test_helpers/."))
    #import the main function
    from main import main
    #import the docker environment
    from util.start_docker_compose import DockerComposeEnvironment

    if __name__ == '__main__':
        #configure the required docker environment
        env = DockerComposeEnvironment(["Device_Registry", "Service_Server", "Dashboard"])
        #start the docker environment
        env.run_docker_compose("./Tutorial/docker-compose.yaml")
        #wait until the server started
        time.sleep(10)
        #run the execution engine
        main()
        #shut down the docker environment
        env.stop_docker_compose()


Here, we first need to add the root directory of the repository to the system path to import the main function of the execution engine. Beside, we can re-use the
docker-environment from the test section.

For this Tutorial, the terminal command must be only requires a device registry, the dashboard and the custom url.


The process can then be executed from the command line with:

.. code-block:: python

    python Tutorial/capability_based_assignment.py "opc.tcp://localhost:4840" "Tutorial/PFDL/capability_based_assignment.pfdl" "dashboard_host_address"="http://localhost:8080" "device_registry_url"="opc.tcp://localhost:8000" "custom_url"="opc.tcp://localhost:" "number_default_clients"=5

so that we can execute the process and map it on the `SWAP-IT Dashboard <https://github.com/iml130/swap-it-dashboard>`_. In case that the log messages of the execution
engine should be captured, the command line argument can be simply adjusted to:

.. code-block:: python

    python Tutorial/capability_based_assignment.py "opc.tcp://localhost:4840" "Tutorial/PFDL/capability_based_assignment.pfdl" "dashboard_host_address"="http://localhost:8080" "log_info"=True "device_registry_url"="opc.tcp://localhost:8000" "custom_url"="opc.tcp://localhost:"
