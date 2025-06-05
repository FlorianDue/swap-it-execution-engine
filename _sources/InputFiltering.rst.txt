..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)


====================
Input Filtering
====================
Since the Control Interface interacts with different entities, such as Device Registries, Assignment Agents or Field level Devices
the Control Interface can filter service specific static input values from the service callback function to set concrete
instances for each. In case that such a value is provided, it replaces global instances, e.g., provided as Execution Engine class arguments,
or dynamic behavior for the resource assignment. In case that a service receives an argument for an Assignment Agent and a Resource Assignment,
the Assignment Agent is ignored and the resource provided with the Resource Assignment argument will be selected to execute the service.

.. _Resources:

Resources
==========

To select a concrete resource to execute the scheduled service, a dispatcher must
provide an Engine Struct *ResourceAssignment* through the list of *input_parameters* to the :ref:`Service Started Callback`.
The Struct contains a single field *job_resource* of type string:

.. code-block:: c

    Struct ResourceAssignment{
        "job_resource":"string"
    }

.. _Capabilities:

Capabilities
============

In case that a target resource is determined by the dynamic :ref:`Resource Assignment` behavior, the Execution Engine
can restrict the resources returned from the Device Registry's Filter_Agent method by providing service specific
capabilities, which are matched against existing capabilities of the Field Level Devices.
To consider such capability restrictions, a dispatcher must
provide an Engine Struct *ServiceName_Capabilities* through the list of *input_parameters* to the :ref:`Service Started Callback`.
Here, the *ServiceName* must correspond to the name argument of the Service started callback. The number of fields can be arbitrary,
however, it must be considered that the `Common Information Model <https://github.com/FraunhoferIOSB/swap-it-common-information-model>`_
restricts the types of capabilities to be matched. The name of each filed of such a *ServiceName_Capabilities* must correspond
to the BrowseName of a Field Leve Device Server. The type of each struct field is a string, independent of whether the
capability is numeric, boolean or string.

.. code-block:: c

    Struct ExampleService_Capabilities{
        "CapabilityName_1":"string",
        "CapabilityName_2":"string",
        ...
    }

.. _Assignment Agents:

Assignment Agents
=====================
To set an Assignment Agent that replaces the Execution Engine's default behavior, or a global Assignment Agent, a dispatcher must
provide an Engine Struct *AssignmentAgent* through the list of *input_parameters* to the :ref:`Service Started Callback`.
The Struct contains a single field *agent* of type string:

.. code-block:: c

    Struct AssignmentAgent{
        "agent":"string"
    }

Device Registry
=====================

To set a Device Registry that replaces the Execution Engine's global Device Registry, a dispatcher must
provide an Engine Struct *DeviceRegistry* through the list of *input_parameters* to the :ref:`Service Started Callback`.
The Struct contains a single field *agent* of type string:

.. code-block:: c

    Struct DeviceRegistry{
        "registry":"string"
    }