import asyncio
import json
import os

import websockets

from pymodbus.client.sync import ModbusSerialClient

from x3emotor import X3EMotor
from MotorAsyncController import MotorAsyncController


async def websocketSender(websocket, motors, motorControllers):
    while True:
        angles = {
            m.id: {
                'angle': m.readAngle() - motorControllers[m.id].startingAngle
            }
            for m in motors.values()
        }
        print(angles)
        await asyncio.wait_for(websocket.send(json.dumps(angles)), 1)
        await asyncio.sleep(0.1)


async def websocketReceiver(websocket, motors, motorControllers):
    async for message in websocket:
        try:
            data = json.loads(message)
            motorId = data['motorId']
            motorControllers[motorId].desiredAngle = int(data['angle']) + motorControllers[motorId].startingAngle
            motorControllers[motorId].desiredP = int(data['P'])
        except Exception as e:
            print(e)


async def websocketHandler(websocket, path):
    global motors, motorControllers
    print("New websocket connection")
    receiverTask = asyncio.ensure_future(
        websocketReceiver(websocket, motors, motorControllers))
    senderTask = asyncio.ensure_future(
        websocketSender(websocket, motors, motorControllers))
    done, pending = await asyncio.wait(
        [receiverTask, senderTask],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


MODBUS_PORT = os.getenv('MODBUS_PORT', default='COM14')
MAIN_MOTOR_ID = 5
STEERING_MOTOR_ID = 4
# one speed unit is ~173 angle units per sec
# 360 degrees is ~4000 angle units

desiredAngle = 0
desiredP = 100
desiredI = 0

client = ModbusSerialClient(method="rtu", port=MODBUS_PORT, stopbits=1,
                            bytesize=8, parity='N', baudrate=115200,
                            timeout=0.1)

mainMotor = X3EMotor(client, id=MAIN_MOTOR_ID)
steeringMotor = X3EMotor(client, id=STEERING_MOTOR_ID)

mainMotorController = MotorAsyncController(mainMotor, 100)
steeringMotorController = MotorAsyncController(steeringMotor, 100)

motors = {
    MAIN_MOTOR_ID: mainMotor,
    STEERING_MOTOR_ID: steeringMotor
}

motorControllers = {
    MAIN_MOTOR_ID: mainMotorController,
    STEERING_MOTOR_ID: steeringMotorController
}

loop = asyncio.get_event_loop()
asyncio.gather(
    websockets.serve(websocketHandler, 'localhost', 8765),
    motorControllers[MAIN_MOTOR_ID].angleTask(),
    motorControllers[MAIN_MOTOR_ID].pTask(),
    motorControllers[MAIN_MOTOR_ID].iTask(),
    motorControllers[STEERING_MOTOR_ID].angleTask(),
    motorControllers[STEERING_MOTOR_ID].pTask(),
    motorControllers[STEERING_MOTOR_ID].iTask(),
)
try:
    pass
    loop.run_forever()
finally:
    for m in motors.values():
        m.release()
    client.close()
    loop.close()
