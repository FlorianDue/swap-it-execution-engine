..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)


.. _Data Object:

=============================
Execution Engine Data Object
=============================
The Data Object manages all tasks and process parameters, which are specified within a process description.
Here, the dispatcher uses the :ref:`Dispatcher Callbacks` to either add Tasks and Variables, or to request Parameter (Figure 1).
The added variables are then read from the Data Object to parameterize services, according to the process description.
Besides values from the Data Object, Services that are executed on the Shop Floor can be parameterizes with literal values.
These literal values are directly declared for a Service within the process description. In addition, Service results from the shop floor
can be utilized to either add new variables or to update variable values within the Data Object.

.. figure:: /images/DataObjectinteraction.png
   :width: 85%
   :alt: Overview

   **Figure 1:** Interaction between the Data Object, the Dispatcher and Resources on the Shop Floor

At the lowest level, each Task within the Data Object is represented as an individual OPC UA Object. The corresponding
ObjectType is illustrated in Figure 2. Each Object has two variables attached by default: the TaskName provides the identifier of the Task
and the StateVariable indicates the current execution status of the corresponding task. In addition, each TaskObject can be extended with an
arbitrary number of variables that are either added to the TaskObject when it is instantiated, or as a result of a Service or Task
execution.

.. _TaskObject:

.. figure:: /images/TaskObject.png
   :width: 25%
   :alt: Overview

   **Figure 2:** TaskObjectType


Figure 3 depicts the different stages of the Data Object on a small PFDL example. The process description features three different types of
variables, the BooleanValue, the NumericValue and the StringValue. In addition, the productionTask of the process features two Tasks, which are executed in parallel:
the loopTask and the simpleTask.

When the Execution Engine starts the process execution, the Data Object is created, featuring only a single TaskObject for the
productionTask. After the Dispatcher schedules the loopTask and the simpleTask, the productionTaskObject within the Data Object is extended with two
corresponding TaskObjects. Since both Tasks feature variables (variable_1 for the loopTask and variable_2, variable_3 for the simpleTask).
the TaskObject is extended with an OPC UA variables that have DataTypes, corresponding to the types of the PFDL process variables.

The loopTask receives variable_1 as input from the productionTask and attaches it to the loopTaskObject. Variable_1 is specified as input and output for the execution of the loop service (Line 20-25). Here,
the value of variable_1 ist first read from the DataObject
and then used to execute the service. As soon as the Service execution completed, the Data Object updates the value of variable_1. Since the loopTask features a Loop Condition based on variable_1 (Line 20)
the Dispatcher needs access to the variable's value to evaluate the condition. Here, the Dispatcher utilizes the :ref:`Data Callback` function to get the current value
of variable_1. In case that the condition is met, the Dispatcher continues scheduling the loop_service. As soon as the condition is not met, the loop is completed, and the Dispatcher
can continue the execution of subsequent Tasks.

The simpleTask receives variable_2 and variable_3 as input from the productionTask. Here, the variables are attached to the
simpleTaskObject and used as input and output for the simple_service (Line 33-34). In addition, the simple_service receives a
literal input that does not appear in the Data Object (Line 35-37). The values of variable_2 and variable_3 are updated after the service execution completes.
Since both variables are defined as Task output, they are transmitted from the simpleTask to the productionTask, as soon as the execution
of the simpleTask completes.

Finally, after the Parallel condition with the loopTask and the simpleTask is completed, the productionTask receives variable_2 and variable_3 as
output and attaches them to its own TaskObject within the Data Object, so that it can be used from the productionTask to either specify input values to services and tasks,
or to evaluate conditions. Furthermore, the loopTaskObject and the simpleTaskObject are removed from the Data Object, so that
only Tasks that are currently executed are represented within the Data Object.

.. figure:: /images/DataObject.png
   :alt: Overview
   :width: 720px

   **Figure 3:** Visualization of the Data Object for an example PFDL process


