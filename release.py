from pymodbus.client.sync import ModbusSerialClient

from x3emotor import X3EMotor

MODBUS_PORT = "/dev/tty.usbserial"

client = ModbusSerialClient(method="rtu", port=MODBUS_PORT, stopbits=1,
                            bytesize=8, parity='N', baudrate=115200,
                            timeout=0.1)

connection = client.connect()
M = X3EMotor(client, 1)

M.release()
