..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)







.. _ Resource Assignment:

=====================
Resource Assignment
=====================
Several approaches can be utilized to find a resource to execute a specified service through the Execution Engine.
Each approach is presented in the following sections and the dominance criteria between these approaches are:

.. code-block:: text

    static resource assignment > service specific resources assignment > global resource assignment > default resource assignment

While the static resource assignment approach specifies a concrete resource to execute the specified service, all
other approaches assign a resource at runtime and are thus, considered as dynamic resource assignment behavior.
All dynamic approaches can consider :ref:`Capabilities`.

Examples for each Resource Assignment can be found in the :ref:`Tutorials`

Static Resource Assignment
===========================
Static Resource Assignment can be accomplished with :ref:`Resources`.

Service Specific Resource Assignment
======================================
Service Specific Resource Assignment can be accomplished with :ref:`Assignment Agents`

Global Resource Assignment
===========================
Global Resource Assignment can be accomplished with the :ref:`Execution Engine Class Argument` *assignment_agent_url* that
deposits an Assignment Agent for the Execution Engine, which is considered for each Resource Assignment that do not include
a Static Resource Assignment or a Service Specific Resource Assignment

Default Resource Assignment
===========================
In case that none of the above presented approaches is configured for an Execution Engine, the Resource Assignment
is accomplished with the Execution Engine's default behaviour. Here, the Execution Engine first requests all available
Resources to execute a service from a Device Registry. Then the Execution Engine checks the number of queue elements
of each Resource and selects the resource with the fewest queue entries.




