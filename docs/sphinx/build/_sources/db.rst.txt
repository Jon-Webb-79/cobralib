**
db
**
The db module can be used to connect to and interact with several relational database
management systems.  Fundamentally this module relies on the **RelationalDB** class
which is a protocol to set the structural sub-typing of all classes that exist
with the protocol.  The base methods and data types are shown below.  However,
certain implimentations for server based relational database management systems
have some methods in excess of what is required by the Protocol.

.. autoclass:: cobralib.db.RelationalDB
   :members:
