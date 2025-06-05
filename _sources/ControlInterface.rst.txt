..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)


.. _Control Interface:

=================
Control Interface
=================

The Control Interface features all functionality that an Execution Engine requires to execute processes on the shop floor.
Figure 1 depicts all of its functional blocks. The Control Interface only comes to play, after the Dispatcher
schedules a service to be executed on the shop floor. After scheduling, the Control Interface first checks, whether a resource,
on which the service should be executed, is provided from the Dispatcher side, or if the Control interface has to detect a resource by itself.
For the latter, the Control Interface connects with a Device Registry to assign the service to a resource. Further information
on the Execution Engine's assignment strategies can be found in the section :ref:`Resource Assignment`.

After the assignment step is completed, an OPC UA client is determined to supervise the service execution. In general,
the Control Interface has a set of clients to execute services. The amount of clients is set at the start of an Execution Engine. In case that
no client is currently available to execute the service, a new client is added to the client list and deployed for the service execution. Besides the set of clients, each
Control Interface features a target server list, where information about each server, a client from the Control Interface has already connected to, are stored.
Such information can be service input and output parameter, as well as the NodeId's of the server's state variable, or the server's service method.
Here, the client first request the information about the target server from the target server list with the GetServer call. In case
that no server is returned from the target server list, the target server must be added to the list with the AddServer call. in this context,
the Control Interface starts a client that connects to the server, browses its address space and adds the server to the target server list.

As next step, the Control interfaces prepares the service execution by connecting a client to the target server. Here, the Control Interface
performs a set of functionalities:

First, the Control Interface checks the Data Object to determine the service input and parameterize the resource with it. In addition, the client
subscribes to the ServiceFinishedEvent of the resource, in case of an asynchronous service result and then calls the Service Method. After the service execution,
the Control Interface receives the service results from either a ServiceFinishedEvent, in case of an asynchronous service result, or the service method,
in case of a synchronous result. Output values specified in the process description are then extracted and added to the Data Object.
Finally, the Service Execution is completed and the Control Interface can place a token for the dispatcher, so that the dispatcher receives a
notification about the completion of the service execution and can continue with the scheduling of the next service.



.. figure:: /images/ControlInterface.png
   :alt: Overview
   :width: 720px

   **Figure 1:** Functionality of the Control Interface


.. toctree::
   :maxdepth: 2

   ResourceAssignment
   InputFiltering