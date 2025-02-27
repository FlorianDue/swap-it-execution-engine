..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)


.. _Service Dispatcher Interaction:

===============================
Service Dispatcher Interaction
===============================

As stated before, the Execution Engine receives notifications about the completion of service executions. Here,
these information are deployed for two functionalities. First, the Execution Engine receives process parameters from the Service execution
as defined in the process description and adds them to the :ref:`Data Object` (1, Figure 1). Second the information about the service completion
is handed over to the dispatcher by setting a Token (2, Figure 1).

Since a single Execution Engine can feature an arbitrary number of Clients is the control interface, the interaction between the Execution Engine
and these Clients is accomplished asynchronously. In addition, each of these Clients runs in a separate thread.

For the asynchronous communication between the Clients and the Execution Engine, the Execution Engine provides the one hand a dictionary
that lists all Services that are currently executed. Each Service in the dictionary is represented by an unique identifier, the context (Task)
of the service execution, a boolean variable that indicates whether the service execution is completed or not, and the name of the service.
As soon as a service execution is started by a Client, the Client adds the service to the dictionary. After the service completion,
the Client sets the boolean variable to TRUE. On the other side, the Execution Engine iterates through the execution dictionary and checks whether
Service executions are completed. If so, the client provides a token to the dispatcher, which then executes the service finished callback, and removes the
Service from the dictionary.

Similar to the execution dictionary, the Execution Engine provides a execution result dictionary. Here, Clients store the results of service executions.
Each result provides the name of the service, its unique identifier, the context (Tasks) of the service execution, a list with output variable
names, as well as a list with the corresponding variable names and variable types. If a client receives results from a service execution,
these results are matched with the specified Service output of the process description. Here, only results that are specified as Service output are
stored in the execution result dictionary.

In contrast to the execution dictionary, the execution result dictionary is not checked during the Execution Engine's main loop. Instead,
the execution result dictionary is checked inside the :ref:`Service Finished Callback`. In case that the Service, for which the Service Finished Callback :ref:`Service Finished Callback`
is executed, is listed within the execution result dictionary, the results from the service are removed from the dictionary and added to the :ref:`Data Object`.





.. figure:: /images/DataObjectEEDispatcher.png
   :alt: Overview
   :width: 100%

   **Figure 1:** Interaction between Dispatcher, Control Interface and Data Object during a Service execution
