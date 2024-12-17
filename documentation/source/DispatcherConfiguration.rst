..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

.. _Dispatcher Configuration:

========================
Dispatcher Configuration
========================
A Dispatcher needs to be configured for the Execution Engine. As default dispatcher, the :ref:`PFDL Scheduler` is deployed. Section :ref:`Custom Dispatcher Integration`
outlines how the :ref:`PFDL Scheduler` can be replaced with a custom dispatcher. Since the dispatcher is an individual software component,
which is loosely coupled to the Execution Engine, the Execution Engine provides a script for a dispatcher `Configuration <https://github.com/FraunhoferIOSB/swap-it-execution-engine/blob/main/dispatcher/dispatcher_configuration.py>`_.
In the `Configuration <https://github.com/FraunhoferIOSB/swap-it-execution-engine/blob/main/dispatcher/dispatcher_configuration.py>`_, a DispatcherConfig class is defined,
which has to be extended with custom code to integrate custom dispatcher. However the DispatcherConfig class pre-defines on the one hand, a minimum set of class variables, and on the other
hand, a config_dispatcher() function. All of the class variables presented in Table 1 must be set with the configuration,
since the Execution Engine accesses these variables during run-time. Besides, the `DispatcherInterface <https://github.com/FraunhoferIOSB/swap-it-execution-engine/blob/main/dispatcher/dispatcher_interface.py>`_
class defines a bunch of setter-function (Table 2), through which either data_types, variable_values, or functions from the dispatcher are made available to the execution engine.

DispatcherConfig Class
======================

The DispatcherConfig class can be extended with any kind of variables and functions, however, only the variables and functions presented below are used by the Execution Engine.

.. code-block:: python

    from dispatcher.dispatcher_interface import DispatcherInterface

    class DispatcherConfig:

        def __init__(self):
            self.dispatcher_object = DispatcherInterface()
            self.structs = []
            self.config_dispatcher()

        def config_dispatcher(self):
            #create and set the instance that will be configured as dispatcher
            self.dispatcher_object.set_dispatcher(...)
            for key,value in ...:
                self.structs.append(...)
            self.dispatcher_object.set_process_parameter(self.structs)
            self.dispatcher_object.set_start_dispatcher(...)
            self.dispatcher_object.set_running(...)
            self.dispatcher_object.set_fire_event_method(...)
            self.dispatcher_object.set_interfaces(...)
            self.dispatcher_object.set_register_dispatcher_callbacks(...)




.. list-table:: **Table 1: DispatcherConfig Class Variables**
   :widths: 50 50 50
   :header-rows: 1

   * - **Variable**
     - **Type**
     - **Explanation**
   * - self.dispatcher_object
     - `DispatcherInterface <https://github.com/FraunhoferIOSB/swap-it-execution-engine/blob/main/dispatcher/dispatcher_interface.py>`_
     - Dispatcher Object instance for the Execution Engine.
   * - self.structs
     - list[:ref:`EngineStruct`]
     - | List with custom variable types in the :ref:`EngineStruct`
       | format. The Execution Engine generates OPC UA
       | :ref:`Data Types` for each type provided in this type list.
   * - self.config_dispatcher()
     - function
     - Configurate the dispatcher for the Execution Engine


.. _DispatcherInterface Setter functions:

.. list-table:: **Table 2: DispatcherInterface Setter functions**
   :widths: 50 100
   :header-rows: 1

   * - **Function**
     - **Explanation**
   * - | set_dispatcher(
       |    *dispatcher: custom_object*
       | )
     - | Hands over the custom dispatcher object to the Execution Engine.
   * - | set_process_parameter(
       |    *structs: :ref:`EngineStruct`*
       | )
     - | Hands over the DispatcherConfig struct variable to the
       | Execution Engine.
   * - | set_fire_event_method(
       |    *fire_event_method: function*
       | )
     - | Hands over a function that is executed whenever the Execution
       | Engine completes a Service execution. This function
       | will be registered as :ref:`Service Finished Event Callback`.
   * - | set_register_dispatcher_callbacks(
       |    *func: function*
       | )
     - | Custom function that registers the :ref:`Dispatcher Callbacks` of the
       | Execution Engine in the custom dispatcher.
   * - | set_start_dispatcher(
       |    *func: function*
       | )
     - | Registers a function inside the Execution Engine that
       | starts the custom dispatcher program.
   * - | set_running(
       |    *func: function*
       | )
     - | Registers a function inside the Execution Engine that returns
       | a boolean value from the dispatcher that indicates whether the
       | dispatcher program is still running or not.


.. _Callback Coupling:
Callback Coupling
=================
Besides registering functions, the DispatcherInterface provides :ref:`Dispatcher Callbacks` that have to be executed from the dispatcher.
Here, two problems might occur. First, the Execution Engine's :ref:`Computational Logic` includes threading and asynchronous function execution,
so that it has to be ensured, that the Execution Engine provides a synchronous interfaces for its callbacks. Second, the callbacks from a custom dispatcher,
which execute the Execution Engine callbacks, might not provide exactly the input that is required by the Execution Engine's callbacks. To solve this (Figure 1), the
Execution Engine provide a set of synchronous callbacks, that wrap the asynchronous callbacks and thus, make them executable for synchronous dispatcher callbacks.
On the side of the custom dispatcher, an applicator might define optional Dispatcher Execution Engine Interfaces. These interfaces are only required in case that the
Dispatcher Callbacks do not provide the required input format for the Execution Engine (for example, an individual format for data types). Here, the Dispatcher
Execution Engine Interface can transform the internal Dispatcher formats to the required Execution Engine format, and besides, ensure, that the required input for the
Execution Engine Callback Wrapper is provided. Further information about the callback coupling can be found in the :ref:`Custom Dispatcher Integration`'s section :ref:`Callbacks`.


.. figure:: /images/Coupling.png
   :alt: Overview
   :width: 100%

   **Figure 1:** Dispatcher Execution Engine Callback Coupling

Mandatory and Optional Callbacks
==================================
As stated before, the Execution Engine only requires a subset of the provided callback functions to be functional. The :ref:`Service Started Callback` and :ref:`Service Finished Callback`
are mandatory since they control the interaction between the Execution Engine and Devices that offer services. Beside, the :ref:`Service Finished Event Callback` communicates the completion of a
service back to the Dispatcher. The other three callbacks are optional. Depending on whether :ref:`Tasks and Services` are utilized or only Service, both, the :ref:`Task Started Callback` and the :ref:`Task Finished Callback`
become mandatory. Independent of Tasks, :ref:`Data Callback` can be realized, so that depending on the Dispatcher Functionality, four combinations of callback functions are possible for an Execution Engine:

.. list-table:: **Table 3: Dispatcher Callback Configurations**
   :widths: 10 100 10 100


   * - | **1**
     - | :ref:`Service Started Callback`
       | :ref:`Service Finished Callback`
       | :ref:`Service Finished Event Callback`
     - | **2**
     - | :ref:`Service Started Callback`
       | :ref:`Service Finished Callback`
       | :ref:`Service Finished Event Callback`
       | :ref:`Data Callback`
   * - | **3**
     - | :ref:`Service Started Callback`
       | :ref:`Service Finished Callback`
       | :ref:`Service Finished Event Callback`
       | :ref:`Task Started Callback`
       | :ref:`Task Finished Callback`
     - | **4**
     - | :ref:`Service Started Callback`
       | :ref:`Service Finished Callback`
       | :ref:`Service Finished Event Callback`
       | :ref:`Task Started Callback`
       | :ref:`Task Finished Callback`
       | :ref:`Data Callback`


