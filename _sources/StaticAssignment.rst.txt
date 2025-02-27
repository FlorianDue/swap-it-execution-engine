..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)





=================
Static Assignment
=================

The `Demonstration Scenario <https://github.com/swap-it/demo-scenario>`_ defines a structure SWAP_Order that must be handed over to each service to be executed.
Here, no additional structure is required, since the assignment strategy of the execution engine completely relies on its default behavior, where the resource,
which has the lowest number of queue elements, is always selected for the service execution. However, the default assignment requires at least
a global defined Device Registry.

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

    #production Task the defines the overall process
    Task productionTask
            #define a single service GetPartsFromWarehouse
       GetPartsFromWarehouse
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
                              "number_light_segments": 1
                    }
                    ResourceAssignment
                    {
                        "job_resource":"opc.tcp://localhost:4080"
                    }

                Out
                    order:SWAP_Order
    End






Process Execution
=================
To execute the above-defined PFDL-process, a small `python script <https://github.com/FraunhoferIOSB/swap-it-execution-engine/blob/main/Tutorial/static_assignment.py>`_ is required to set up the execution engine and the docker environment:

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
        env = DockerComposeEnvironment(["Service_Server", "Dashboard"])
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

The process can then be executed from the command line with:

.. code-block:: python

    python Tutorial/static_assignment.py "opc.tcp://localhost:4840" "Tutorial/PFDL/static_assignment.pfdl" "dashboard_host_address"="http://localhost:8080"

so that we can execute the process and map it on the `SWAP-IT Dashboard <https://github.com/iml130/swap-it-dashboard>`_. In case that the log messages of the execution
engine should be captured, the command line argument can be simply adjusted to:

.. code-block:: python

    python Tutorial/static_assignment.py "opc.tcp://localhost:4840" "Tutorial/PFDL/static_assignment.pfdl" "dashboard_host_address"="http://localhost:8080" "log_info"=True
