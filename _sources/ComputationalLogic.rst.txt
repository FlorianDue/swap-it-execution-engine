..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

.. _Computational Logic:

Computational Logic
====================
To get a better understanding of the operational logic of an Execution Engine, Figure 1 illustrates its computational logic.
The OPC UA Server of the Execution, as well as its OPC UA Clients are implemented with the `open source Python asyncio Stack <https://github.com/FreeOpcUa/opcua-asyncio>`_,
which uses with `asyncio <https://docs.python.org/3/library/asyncio.html>`_ asynchronous programming. Here, an
EventLoop allows the managing and distributed execution of different operations. However, to effectively execute the separated Client and Server Loops, the Execution Engine's
OPC UA Server is executed in a main thread and each Client is started in a separate thread with an individual EventLoop.

While the `open source Python asyncio Stack <https://github.com/FreeOpcUa/opcua-asyncio>`_ completely relies on asynchronous programming, a custom dispatcher implementation may not,
so that it is required to invoke asynchronous operations (Callbacks Dispatcher Interface) from synchronous operations (Dispatcher). Here, the `Python nest_asyncio <https://github.com/erdewit/nest_asyncio>`_
library allows the nesting of asyncio EventLoops, so that a Dispatcher invocation of an Execution Engine callback is accomplished with a wrapper function that only starts a nested EventLoop,
which then executes the actual callback of the dispatcher interface.

The separate processing of the different program functionalities requires interfaces between them to make data available between different EventLoops and threads.
Here, the nested EventLoops of the Dispatcher interface Callbacks can directly interact with the Main Loop of the OPC UA Server and thus, perform operations on the OPC UA Server,
such as the adding or removing of variables and objects, or the reading and writing of variable values.

Since OPC UA Clients of the Control Interface are started from the Dispatcher Interface's *Service Started Callback*, the `Python queue <https://docs.python.org/3/library/queue.html>`_
library is deployed to ensure a safe exchange of information between the different threads. On the other side, the Main Thread receives information from the Control Interface about the completion of services,
as well as the provision of execution parameter. Here a *Semaphore* between the different threads is utilized, where the Control Interfaces adds elements to either the service execution list or the Execution Parameter List. The Main Thread,
checks at each iteration whether elements were added to the list or not. If so, the Main Thread can access these information through the callbacks or the OPC UA Server and react to their occurrence.


.. figure:: /images/ComputationalLogic.png
   :alt: Overview
   :width: 100%

   **Figure 1:** Computational Logic of the Execution Engine