..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

.. _Execution Engine Logic:

===========================
Execution Engine Logic
===========================

The logic of the Execution Engine includes the OPC UA server of the Execution Engine, which in turn,
features the :ref:`Data Object` (1 in Figure 1). Since the DataObject provides all input and output parameter for processes,
corresponding OPC UA data types are required for the server (2 in Figure 1). Here, the Execution Engine provides an interface
to generate the corresponding :ref:`Data Types`. Tasks (3 in Figure 1) and Service Results (5 in Figure 1)
are added and remove from the Data Object as described in :ref:`Data Object`. Lastly, the Execution Engine receives notification about the
completion of service executions (4 in Figure 1) and transmits them to the Dispatcher, which in turn can trigger transitions of the process control
and thus, schedule further services. Further information regarding the interaction between Execution Engine, Dispatcher and the Control interface
can be found in section :ref:`Service Dispatcher Interaction`.






.. figure:: /images/execution_engine_logic.png
   :alt: Overview
   :width: 100%

   **Figure 1:** Functional entities of the Execution Engine Logic


.. toctree::
   :maxdepth: 2

   DataObject
   GenerateOPCUATypes
   ServiceInterface