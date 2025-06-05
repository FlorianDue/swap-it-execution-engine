..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

.. _Dispatcher Callbacks:

======================
Dispatcher Callbacks
======================
The Execution Engine's Dispatcher Interface provides six callback functions in total. Their purpose and API is explained in the following sections:

 - :ref:`Service Started Callback`
 - :ref:`Service Finished Callback`
 - :ref:`Task Started Callback`
 - :ref:`Task Finished Callback`
 - :ref:`Data Callback`
 - :ref:`Service Finished Event Callback`

These callbacks are not called from the Execution Engine, but from the integrated dispatcher. That means, the dispatcher controls the behavior of the Execution Engine,
which only reacts to the invocation of the callbacks. (besides the Service Finished Event Callback)


From these six callback, the execution engine only requires the :ref:`Service Started Callback`, :ref:`Service Finished Callback` and the :ref:`Service Finished Event Callback`
to execute processes. The additional callbacks are optional and only need to be considered, in case that it is required by the custom dispatcher.


.. _Service Started Callback:

Service Started Callback
========================

The Service Started Callback is executed to start a service execution and takes a OPC UA Client from the Execution Engine's Control Interface, which the connects to a
target resource and executes the specified service. The Service Started Callback requires the following input parameter:

.. list-table:: **Service Started Callback**
   :widths: 50 50 50
   :header-rows: 1

   * - **Argument**
     - **Type**
     - **Explanation**
   * - name
     - str
     - Name of the Service to be executed
   * - service_uuid
     - str
     - UUID that uniquely identifies the Service
   * - task_context_uuid
     - str
     - | UUID of the context (a Task) in which the
       | Service is started
   * - input_parameters
     - list[union(str, :ref:`EngineStruct`, list[str])]
     - | List with input parameters. Each List element is
       | either a string with a variable name that should
       | be read from the :ref:`Data Object`
       | or a literal value that is provided in the
       | :ref:`EngineStruct` format.
       | It's possible to hand over an empty list.
       | It's also possible to hand over a "browse
       | list" to access a field of a structure type.
       | For example with ["value", "field", "[10]"],
       | the input value is the "10th" element of the
       | array "field" in the structure "value".
   * - output_parameters
     - ordered_dictionary
     - | Ordered Dictionary that specifies all output
       | parameter that should be returned from a Service.
       | The ordered dict contains strings in the format
       | OrderedDict([(variable_name, data_type_name)])

.. _Service Finished Callback:

Service Finished Callback
=========================

The Service finished callback is executed after the completion of a Service execution and attaches output
variables from the service execution to the :ref:`Data Object`. It requires the following input arguments:

.. list-table:: **Service Finished Callback**
   :widths: 50 50 50
   :header-rows: 1

   * - **Argument**
     - **Type**
     - **Explanation**
   * - name
     - str
     - Name of the Service that is finished
   * - task_context_uuid
     - str
     - | UUID of the context (a Task) in which the
       | Service is finished
   * - service_uuid
     - str
     - UUID that uniquely identifies the Service


.. _Task Started Callback:

Task Started Callback
=========================

The Task Started Callback is executed to add :ref:`TaskObject` to the :ref:`Data Object`. In this context, specified input variables are attached to the
newly added :ref:`TaskObject`. It requires the following input arguments:

.. list-table:: **Task Started Callback**
   :widths: 50 50 50
   :header-rows: 1

   * - **Argument**
     - **Type**
     - **Explanation**
   * - task_name
     - str
     - Name of the Task to be executed.
   * - task_uuid
     - str
     - | UUID that uniquely identifies
       | the Task.
   * - task_context_uuid
     - str
     - | UUID of the context (a Task) in which
       | the Task is started
   * - task_input_parameter_names
     - ordered_dictionary
     - | Ordered Dictionary that specifies all
       | input parameter that should be added
       | to the Task. The ordered dict contains
       | a list with strings in the format:
       | OrderedDict([(variable_name,
       | data_type_name)])
   * - task_input_parameter_instances
     - list[union(str, :ref:`EngineStruct`, list[str])]
     - | List with input parameters. Each List
       | element is either a string with a variable
       | name that should be read from the
       | :ref:`Data Object`
       | or a literal value that is provided in
       | the :ref:`EngineStruct` format.
       | It's possible to hand over an empty list.
       | It's also possible to hand over a "browse
       | list" to access a field of a structure type.
       | For example with ["value", "field", "[10]"],
       | the input value is the "10th" element of the
       | array "field" in the structure "value".


.. _Task Finished Callback:

Task Finished Callback
=========================
The Task Finished Callback is executed to remove :ref:`TaskObject` from the :ref:`Data Object`. In this context, specified output variables are extracted and added to the
Tasks Context's :ref:`TaskObject`. It requires the following input arguments:

.. list-table:: **Task Finished Callback**
   :widths: 50 50 50
   :header-rows: 1

   * - **Argument**
     - **Type**
     - **Explanation**
   * - name
     - str
     - Name of the Task that is finished
   * - uuid
     - str
     - UUID that uniquely identifies the Task
   * - task_context_uuid
     - str
     - | UUID of the context (a Task) in which the
       | Service is finished
   * - output_parameter
     - list[str]
     - | List with variable names. Each listed variable read
       | from the current Task and attached to the Task context.
       | It's possible to hand over an empty list.



.. _Data Callback:

Data Callback
==============
The Data Callback is executed to return a variable from the :ref:`Data Object` to the dispatcher. It requires the following input arguments:

.. list-table:: **Data Callback**
   :widths: 50 50 50
   :header-rows: 1

   * - **Argument**
     - **Type**
     - **Explanation**
   * - variable_name
     - str
     - Name of the variable, which value should be returned to the dispatcher.
   * - task_id
     - str
     - | UUID that uniquely identifies
       | the Task from which the variable should be read.


.. _Service Finished Event Callback:

Service Finished Event Callback
===============================

In contrast to the other callbacks, the Service Finished Event Callback is actively triggered from the Execution Engine.
Here the Service Finished Event Callback provides information to the dispatcher that a service execution was completed.
It requires the following input arguments:

.. list-table:: **Service Finished Event Callback**
   :widths: 50 50 50
   :header-rows: 1

   * - **Argument**
     - **Type**
     - **Explanation**
   * - service_uuid
     - str
     - UUID of the service, which execution is completed.
