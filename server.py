import asyncio
import os

import websockets

from pymodbus.client.sync import ModbusSerialClient

from x3emotor import X3EMotor


async def setAngleSlowly(max_speed=20):
    global desiredAngle
    while True:
        prevDesiredAngle = desiredAngle
        flag = False
        while desiredAngle == prevDesiredAngle:
            currentAngle = M.readAngle()
            dist = abs(currentAngle - desiredAngle)
            if flag:
                pass
            elif dist < 500:
                M.setAngle(desiredAngle)
                flag = True
            # else:
            #     K = 0.05
            #     print("V:", min(max_speed, dist*K))
            #     M.setSpeed(-min(max_speed, dist*K) if desiredAngle < currentAngle else min(max_speed, dist*K))
            elif dist < max_speed * 30:
                M.setSpeed(-5 if desiredAngle < currentAngle else 5)
            else:
                M.setSpeed(-max_speed if desiredAngle < currentAngle else max_speed)
            await asyncio.sleep(0.01)


async def websocketSender(websocket):
    global M
    while True:
        angle = M.readAngle()
        print(angle)
        await asyncio.wait_for(websocket.send(str(angle)), 1)
        await asyncio.sleep(0.1)


async def websocketReceiver(websocket):
    global desiredAngle
    async for message in websocket:
        try:
            desiredAngle = int(message)
            print("New desired angle:", desiredAngle)
        except ValueError as e:
            print(e)


async def websocketHandler(websocket, path):
    print("New websocket connection")
    receiverTask = asyncio.ensure_future(
        websocketReceiver(websocket))
    senderTask = asyncio.ensure_future(
        websocketSender(websocket))
    done, pending = await asyncio.wait(
        [receiverTask, senderTask],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


def setup():
    global M
    M.writeRegister(16, 500)  # P
    M.writeRegister(15, 0)  # I


MODBUS_PORT = os.getenv('MODBUS_PORT', default='COM14')
# one speed unit is ~173 angle units per sec
# 360 degrees is ~4000 angle units

desiredAngle = 0

client = ModbusSerialClient(method="rtu", port=MODBUS_PORT, stopbits=1,
                            bytesize=8, parity='N', baudrate=115200,
                            timeout=0.1)
M = X3EMotor(client, 1)

setup()

loop = asyncio.get_event_loop()
loop.run_until_complete(websockets.serve(websocketHandler, 'localhost', 8765))
asyncio.gather(
    setAngleSlowly()
)
try:
    pass
    loop.run_forever()
finally:
    M.release()
    client.close()
    loop.close()
