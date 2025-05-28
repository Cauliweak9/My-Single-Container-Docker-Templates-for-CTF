#  Modbus Docker Template

##  Intro  简介

This template uses `pymodbus` library to simulate a Modbus server and several slaves. Both the Modbus server and verification uses the same port, so port forwarding is used.

这个模板使用`pymodbus`库以模拟Modbus服务器和从机。Modbus服务器和验证均使用同一个端口，因此使用了端口转发。



This template uses Modbus TCP/IP protocol, so the protocol identifier will always be `\x00\x00`, and this is how I tell the difference between a Modbus query and a non-Modbus query.

这个模板使用的是Modbus TCP/IP协议，因此协议标识符永远为`\x00\x00`，而这也是我如何区分Modbus请求和一个非Modbus请求的。

##  server.py

This is where the Modbus server and slaves are created. Each slave can hold up to 4 data blocks (`co` for Coils, `hr` for Holding Registers, `ir` for Input Registers and `di` for Discrete Inputs if I'm not mistaken), and the `0x**` is the device ID for the slave

这里是Modbus服务器和从机创建的地方，每个从机最多可以持有4个数据块，对应Modbus的4种数据类型，而后面的`0x**`是设备ID

##  client.py

The main logic is here, including PLC logic implementation, port forwarding, multi-thread interaction etc. The hardest part of making a challenge like this is to build your own PLC and implement your logic. Here I used a pretty dumb but useful way: Implementing each PLC logic whenever a Modbus Write method is called to simulate a real-time reaction.

这里是主逻辑，包括PLC逻辑实现、端口转发、多线程交互等。出这么一道题最难的点在于自己设计并实现PLC。这里我用了一个非常笨但是有用的方法：在每一次Modbus写入操作后去实现PLC的逻辑以模拟一个实时的反应。

