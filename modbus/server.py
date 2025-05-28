from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock

def run_server():
    # 创建寄存器从机
    register_block = ModbusSequentialDataBlock.create()
    register_slave = ModbusSlaveContext(hr=register_block)
    # 创建线圈从机
    coil_block = ModbusSequentialDataBlock.create()
    coil_slave = ModbusSlaveContext(co=coil_block)
    # 创建Modbus服务器，使用不同的设备ID指向不同的从机
    context = ModbusServerContext(slaves={0x74: register_slave, 0x31: coil_slave}, single=False)
    StartTcpServer(context=context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    run_server()