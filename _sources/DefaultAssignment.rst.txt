..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)





=========================
Default Assignment
=========================


The `Demonstration Scenario <https://github.com/swap-it/demo-scenario>`_ defines a structure SWAP_Order that must be handed over to each service to be executed.
For the Default Assignment, a Device Registry is required. However, instead of an external Assignment Agent, the default assignment behavior of the execution engine is deployed.

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

    Task productionTask
        Parallel
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
            manufacture_stand_segment
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
                Out
                    order:SWAP_Order
        Mounting
            In
                order
            Out
                order:SWAP_Order
    End


    Task manufacture_stand_segment
        In
            order: SWAP_Order
        GetPartsFromWarehouse
            In
                order
            Out
                order: SWAP_Order
        Milling
            In
                order
            Out
                order:SWAP_Order
        Out
            order
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
            Out
                order: SWAP_Order
        Out
            order
    End



Process Execution
=================
To execute the above-defined PFDL-process, a small `python script <https://github.com/FraunhoferIOSB/swap-it-execution-engine/blob/main/Tutorial/default_assignment.py>`_ is required to set up the execution engine and the docker environment:

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

For this Tutorial, the terminal command must be extended with two of the optional arguments. First, a global Device Registry is set with the argument *"device_registry_url"="opc.tcp://localhost:8000"*. Besides,
each service server registers itself in the Device Registry with the URI from the docker compose environment, so that the URI returned from the
Device Registry must ab adjusted, to replace the docker-internal URI with a docker-external URI. Here, the optional argument *"custom_url"="opc.tcp://localhost:"* is added, so that each server from the
docker-environment can be reached from outside.

The process can then be executed from the command line with:

.. code-block:: python

    python Tutorial/default_assignment.py "opc.tcp://localhost:4840" "Tutorial/PFDL/default_assignment.pfdl" "dashboard_host_address"="http://localhost:8080" "device_registry_url"="opc.tcp://localhost:8000" "custom_url"="opc.tcp://localhost:"

so that we can execute the process and map it on the `SWAP-IT Dashboard <https://github.com/iml130/swap-it-dashboard>`_. In case that the log messages of the execution
engine should be captured, the command line argument can be simply adjusted to:

.. code-block:: python

    python Tutorial/default_assignment.py "opc.tcp://localhost:4840" "Tutorial/PFDL/default_assignment.pfdl" "dashboard_host_address"="http://localhost:8080" "log_info"=True "device_registry_url"="opc.tcp://localhost:8000" "custom_url"="opc.tcp://localhost:"
