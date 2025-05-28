import socket
from threading import Thread
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
import random

# 配置参数
MODBUS_SERVER_HOST = '127.0.0.1'
MODBUS_SERVER_PORT = 502
PROXY_PORT = 504         # 代理监听端口
STATUS_SLAVE = 0x31      # 设备ID
FUEL_SLAVE = 0x74
STATUS_COILS = {"Auto Mode":0x0721, "Manual-Initialize":0x1337,"Manual Mode":0x2085,"Use Backup":0x3137, "Main Power":0x7137,"Backup Power":0x7331,"Fuel System":0x8848,"Power System":0xbeaf,"Propulsion System":0xdead} # 状态线圈地址
# 按顺序：Auto-Mode, Manual-Init, Manual-Mode, Use-Backup, Main-Power, Backup-Power, Power-System, Propulsion-System
current_status = [True, False, False, False, False, False, False, False]
# 预期解
INTENTIONAL_STATUS = [False, True, True, True, False, True, True, True]
# 燃料系统配置
FUEL_POINTER = 0x3000
FUEL_DEVICE_START = 0x6000
fuel_system = False
FLAG = "Aurora{Looking into the distance, a home I can never return to...}"

def handle_logic(data:bytes):
    device_id = data[6]
    function_id = data[7]
    global fuel_system
    # 无写入操作就无需进入逻辑处理
    if device_id not in [STATUS_SLAVE, FUEL_SLAVE] or function_id not in [5,6,15,16,22,23]:
        return
    with ModbusTcpClient(MODBUS_SERVER_HOST, port=MODBUS_SERVER_PORT) as mb_client:
        # 线圈操作
        if device_id == 0x31:
            status = []
            for value in STATUS_COILS.values():
                # 跳过燃料系统
                if value == 0x8848:
                    continue
                coil_status = mb_client.read_coils(address=value, count=1,slave=STATUS_SLAVE)
                status.append(coil_status.bits[0])
            print(status)
            # 执行第1~2行梯形图判断：开启手动模式
            if status[0] and status[1] and not status[2]:
                status[0] = False
                status[2] = True
                mb_client.write_coil(address=STATUS_COILS["Auto Mode"], value=False, slave=STATUS_SLAVE)
                mb_client.write_coil(address=STATUS_COILS["Manual Mode"], value=True, slave=STATUS_SLAVE)
            # 第2行梯形图拓展：关闭手动初始化时关闭手动模式并自动开启自动模式
            if not status[1]:
                status[0] = True
                status[2] = False
                mb_client.write_coil(address=STATUS_COILS["Auto Mode"], value=True, slave=STATUS_SLAVE)
                mb_client.write_coil(address=STATUS_COILS["Manual Mode"], value=False, slave=STATUS_SLAVE)
            # 第4行梯形图：启用备用电源
            if status[2] and status[3] and not status[5]:
                status[5] = True
                mb_client.write_coil(address=STATUS_COILS["Backup Power"], value=True, slave=STATUS_SLAVE)
            # 第5行梯形图：非手动模式自动重置备用电源的启用
            if not status[2]:
                status[3] = False
                mb_client.write_coil(address=STATUS_COILS["Use Backup"], value=False, slave=STATUS_SLAVE)
            # 第6行梯形图：能源系统OK
            if status[4] or status[5]:
                status[6] = True
                mb_client.write_coil(address=STATUS_COILS["Power System"], value=True, slave=STATUS_SLAVE)
            print(status)
            for i in range(8):
                current_status[i] = status[i]
        # 寄存器操作
        elif device_id == 0x74:
            # 获取指向的燃料舱
            result = mb_client.read_holding_registers(address=FUEL_POINTER, count=1, slave=FUEL_SLAVE)
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
            fuel_device_id = decoder.decode_16bit_int()
            print(fuel_device_id)
            # 获取燃料舱中含有的燃料量
            result = mb_client.read_holding_registers(address=FUEL_DEVICE_START+fuel_device_id-1, count=1, slave=FUEL_SLAVE)
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
            fuel_amount = decoder.decode_16bit_int()
            print(fuel_amount)
            # 判断燃料量并进行线圈操作
            if fuel_amount >= 75:
                fuel_system = True
                mb_client.write_coil(address=STATUS_COILS["Fuel System"], value=True, slave=STATUS_SLAVE)
            else:
                fuel_system = False
                mb_client.write_coil(address=STATUS_COILS["Fuel System"], value=False, slave=STATUS_SLAVE)
        # 最后一行梯形图：推进系统OK
        if fuel_system and current_status[6]:
            current_status[7] = True
            mb_client.write_coil(address=STATUS_COILS["Propulsion System"], value=True, slave=STATUS_SLAVE)

def check_status(client_socket):
    # 检查状态线圈值
    resp = f"Auto Mode: {current_status[0]}, Manual Mode: {current_status[2]}, Main Power: {current_status[4]}, Backup Power: {current_status[5]}, Power System: {current_status[6]}, Fuel System: {fuel_system}, Propulsion System: {current_status[7]}\n"
    if current_status[7] == True:
        if current_status == INTENTIONAL_STATUS:
            resp = resp + f"Congratulations, your rocket is now able to be launched!\nHere's your flag: {FLAG}\n"
        else:
            resp = resp + f"I don't know how you did it, but your rocket seems to be able to be launched...? Good luck taking your journey back...\nHere's your flag: {FLAG}\n"
    client_socket.send(resp.encode())

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                return

            # 判断是否为Modbus请求（检查事务ID和协议标识符）
            if len(data) >= 6 and data[2:4] == b'\x00\x00':
                # 转发到Modbus服务器
                with ModbusTcpClient(MODBUS_SERVER_HOST, port=MODBUS_SERVER_PORT) as mb_client:
                    mb_client.socket.send(data)
                    response = mb_client.socket.recv(1024)
                    client_socket.send(response)
                    # 用户执行完操作后进行PLC逻辑实现
                    handle_logic(data)
            elif data.strip().lower() == b'status':
                check_status(client_socket)
            else:
                client_socket.send(b"Unknown request data")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        client_socket.close()

def run_proxy_server():
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.bind(('0.0.0.0', PROXY_PORT))
    proxy.listen(5)
    print(f"[*] Listening on port {PROXY_PORT}")

    while True:
        client_sock, addr = proxy.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        # 一个端口支持多个线程的连接，可以同时nc和mbpoll
        handler = Thread(target=handle_client, args=(client_sock,))
        handler.start()

if __name__ == "__main__":
    # 初始化设置（仅首次运行）
    try:
        with ModbusTcpClient(MODBUS_SERVER_HOST, port=MODBUS_SERVER_PORT) as client:
            # 选择任意1个燃料舱
            selected_device = random.randint(0,3)
            for i in range(4):
                # 设置燃料舱燃料并写入
                if i != selected_device:
                    amount = random.randint(1,74)
                else:
                    amount = random.randint(75,100)
                builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
                builder.add_16bit_int(amount)
                # print(builder.to_registers())
                client.write_registers(address=FUEL_DEVICE_START+i, values=builder.to_registers(), slave=FUEL_SLAVE)
            print("[*] Initialized fuel registers")
            # 首先开启自动模式
            client.write_coil(address=STATUS_COILS["Auto Mode"], value=True, slave=STATUS_SLAVE)
            print("[*] Initialized status coils")
    except Exception as e:
        print(f"Initialization failed: {e}")

    # 启动代理服务器
    run_proxy_server()