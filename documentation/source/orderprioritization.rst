..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2025 (c) Fraunhofer IOSB (Author: Florian Düwel)


.. _Order Prioritization:

========================
Order Prioritization
========================
The Execution Engine provides optional arguments for an order prioritization. Here, a concrete prioritization value can be set, together with an
url of an prioritization module.

Concept
========
If such arguments are provided, the execution engine automatically registers itself within the prioritization module.
As consequence, the prioritization module will then check the Job Queues of each resource and re-orders these queues, based on the prioritization values
of the different execution engines (see Figure 1). Here The Prioritization Module frequently browses a registry module for available shop floor resources.
Each resources then get a prioritization list, where all execution engines with corresponding order priorities are listed. Based on this list,
the resource re-orders its job queue, so that jobs with a lower prioritization are executed before jobs with a higher value. However, the priority value must be larger than 0 to be considered.


.. figure:: /images/orderprioritization.png
   :alt: Overview
   :width: 720px

   **Figure 1:** Overview Order Prioritization


Using the Provided Prioritization Module
================================================
This repository provides an example implementation of such an prioritization module. It can be found in the directory **external_modules/order_prioritizer** and can be
started with the **start_order_prioritizer.py** script. Here, the order prioritization module requires five arguments, from which the custom_url and the waiting_time argument are optional:

- **url:** URL of the OPC UA Server that will be started
- **port:** Port of the OPC UA Server that will be started
- **device_registry_url:** URL and Port of the device registry, to which the prioritization module connects itself to find resources on the shop floor. All resources, which are registered in the device registry will receive the priority list of the prioritization module
- **custom_url:** The custom URL replaces the url of the servers that where extracted from the device registry. This is relevant e.g., when an simulation environment runs inside docker containers
- **waiting_time**: Time the prioritization module waits until it re-browses the device registry to find new servers, as well as the time it waits until a new priority list is handed over to the resources. Defaults to 5 seconds.
