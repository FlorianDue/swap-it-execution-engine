..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

.. _Dispatcher Interface:

=======================
Dispatcher Interface
=======================

The Execution Engine provides a Dispatcher Interface to integrate custom scheduler to execute processes. Here the Execution
Engine offers six :ref:`Dispatcher Callbacks` to start and finish Services and Tasks, fire Service Finished Events and a
Data Callback to provide process parameter to a scheduler (Figure 1).

.. figure:: /images/DispatcherInterface.png
   :alt: Overview
   :width: 50%

   **Figure 1:** Dispatcher Interface


We connect the `PFDL-Scheduler <https://github.com/iml130/pfdl>`_ as default dispatcher to the Execution Engine. However,
the Execution Engine provides a set of APIs to integrate custom schedulers.
Section :ref:`Dispatcher Configuration` outlines how the `PFDL-Scheduler <https://github.com/iml130/pfdl>`_ is configured as Dispatcher for
our default implementation in this repository. More information about the
custom integration of individual Dispatcher and the required Execution Engine APIs are provided in section :ref:`Custom Dispatcher Integration`.



.. toctree::
   :maxdepth: 2

   ComputationalLogic
   DispatcherCallbacks
   DispatcherConfiguration
   CustomDispatcherIntegration

