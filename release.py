import os

from pymodbus.client.sync import ModbusSerialClient

from x3emotor import X3EMotor

MODBUS_PORT =  os.getenv('MODBUS_PORT', default='COM14')

client = ModbusSerialClient(method="rtu", port=MODBUS_PORT, stopbits=1,
                            bytesize=8, parity='N', baudrate=115200,
                            timeout=0.1)

connection = client.connect()
for i in 4, 5:
    M = X3EMotor(client, i)
    M.release()

client.close()
