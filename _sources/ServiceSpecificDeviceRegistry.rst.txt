..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)





==================================
Service Specific Device Registry
==================================


The `Demonstration Scenario <https://github.com/swap-it/demo-scenario>`_ defines a structure SWAP_Order that must be handed over to each service to be executed.
For the Service Specific Device Registry, a device registry will be locally registered in the execution engine for a single service,
so that it is considered only there. The remaining assignment steps are accomplished with the static assignment strategy of the execution engine.
Consequently, an *DeviceRegistry* and a *ResourceAssignment* structure must be defined in the PFDL.


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

    Struct ResourceAssignment
            job_resource:string
    End

    Struct DeviceRegistry
            registry:string
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
                            DeviceRegistry
                            {
                                "registry":"opc.tcp://localhost:8000"
                            }
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
                        ResourceAssignment
                        {
                            "job_resource":"opc.tcp://localhost:4080"
                        }
                    Out
                        order: SWAP_Order
                Coating
                    In
                        order
                        ResourceAssignment
                        {
                            "job_resource":"opc.tcp://localhost:4091"
                        }
                    Out
                        order: SWAP_Order
                Out
                    order
    End



Process Execution
=================
To execute the above-defined PFDL-process, a small `python script <https://github.com/FraunhoferIOSB/swap-it-execution-engine/blob/main/Tutorial/service_specific_device_registry.py>`_
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

Since the Device registry is registered locally, it can be removed as program argument. Consequently, he process can then be executed from the command line with:

.. code-block:: python

    python Tutorial/service_specific_device_registry.py "opc.tcp://localhost:4840" "Tutorial/PFDL/service_specific_device_registry.pfdl" "dashboard_host_address"="http://localhost:8080" "custom_url"="opc.tcp://localhost:"

so that we can execute the process and map it on the `SWAP-IT Dashboard <https://github.com/iml130/swap-it-dashboard>`_. In case that the log messages of the execution
engine should be captured, the command line argument can be simply adjusted to:

.. code-block:: python

    python Tutorial/service_specific_device_registry.py "opc.tcp://localhost:4840" "Tutorial/PFDL/service_specific_device_registry.pfdl" "dashboard_host_address"="http://localhost:8080" "log_info"=True  "custom_url"="opc.tcp://localhost:"
