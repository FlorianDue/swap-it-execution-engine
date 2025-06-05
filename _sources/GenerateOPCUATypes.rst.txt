..
    Licensed under the MIT License.
    For details on the licensing terms, see the LICENSE file.
    SPDX-License-Identifier: MIT

    Copyright 2023-2024 (c) Fraunhofer IOSB (Author: Florian Düwel)

.. _Data Types:

==========
Data Types
==========
The Execution Engine features two kind of data type definitions. First, the Execution Engine has an internal data format, which is used
to exchange parameter between the Execution Engine and Schedulers, which are attached trough the Dispatcher. Second, the data type of each parameter
that is defined as part of the process description, is translated into a corresponding OPC UA data type. These OPC UA Types are required to add variables to the :ref:`Data Object`,
to generate the input for the Service Methods and to extract the received service results from the resource server.

.. _Internal Execution Engine Types:

Internal Execution Engine Types
================================
The internal Execution Engine types are mainly required for the interface between a custom scheduler and the Dispatcher.
Here these internal data types enable a standardized format for the exchange of parameter. Since the Execution Engine generates custom OPC UA
data types from the custom type definitions, each type is declared as a custom structure and it is not possible to directly declare single variables.
Here the definition of a simple string variable cannot be accomplished with *string_variable = "TestString"*.
Instead, the *string_variable* must be declared as a field of a structure, e.g.:

*StringStructure{string_variable = "TestString"}*

The Execution Engine provides individual Python objects to define structures in the Execution Engine format:


.. _EngineStruct:

.. list-table:: **EngineStruct**
   :widths: 50 50
   :header-rows: 1

   * - EngineStruct
     -
   * - Name
     - Name of the Structure
   * - DataType
     - Data Type of the Structure
   * - Attributes
     - | Fields of the Structure. Each Attribute can either be an individual :ref:`EngineStruct`,
       | :ref:`EngineArray` or a :ref:`SimpleType` such as a String, a Integer, or a Boolean.


.. _EngineArray:

.. list-table:: **EngineArray**
   :widths: 50 50
   :header-rows: 1

   * - EngineArray
     -
   * - Name
     - Name of the array
   * - DataType
     - Data Type of the Array elements. Data Types can either be :ref:`EngineStruct` or :ref:`SimpleType`.
   * - Length
     - | Number of Array elements. In case of arrays with an unspecific length,
       | the value has to be set to -1
   * - Values
     - Elements of the array, in case that it is not empty



Simple types are ordinary data types. However, since these data types are converted into OPC UA Types, the supported simple types are a subset of the
`Build-in OPC UA Data Types <https://reference.opcfoundation.org/Core/Part6/v104/docs/5.1.2>`_.
The list with currently supported simple types is shown in the table below. In this context, the *Type* indicates the Data Type
and the Key the name that is required as EngineStruct data type, to identify the corresponding type.

.. _SimpleType:

.. list-table:: **SimpleTypes**
   :widths: 50 50
   :header-rows: 1

   * - Type
     - Key
   * - String
     - string
   * - Boolean
     - boolean
   * - Double
     - number

.. _Data Converter:

Data Converter
==============
The Execution Engine has two build-in data converter. The first takes instances of EngineStructs and converts
them to OPC UA variables with custom structure data types. The second takes OPC UA variables and generates EngineStructs out of it.

.. _Custom OPC UA Types:

Custom OPC UA Types
====================
Lastly, when an Execution Engine is started, it must generate OPC UA Data Types out of the parameter type definitions of a process description.
Here, a list with all custom type definitions for a process must be handed over from the process description to the Execution Engine at the
beginning of the process execution. All custom data types must be provided in the :ref:`EngineStruct` format.

