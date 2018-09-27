import asyncio
import json
import os

import websockets

from pymodbus.client.sync import ModbusSerialClient

from x3emotor import X3EMotor


async def setAngle(max_speed=20):
    global desiredAngle
    while True:
        print("New desired angle:", desiredAngle)
        prevDesiredAngle = desiredAngle
        finished = False
        while desiredAngle == prevDesiredAngle:
            currentAngle = M.readAngle()
            dist = abs(currentAngle - desiredAngle)
            if finished:
                pass
            elif dist < 500:
                M.setAngle(desiredAngle)
                finished = True
            elif dist < max_speed * 30:
                M.setSpeed(-5 if desiredAngle < currentAngle else 5)
            else:
                M.setSpeed(-max_speed if desiredAngle < currentAngle else max_speed)
            await asyncio.sleep(0.01)

async def setP():
    global desiredP, M
    M.writeRegister(16, desiredP)
    currentP = desiredP
    while True:
        if desiredP != currentP:
            print("New desired P:", desiredP)
            M.writeRegister(16, desiredP)
            currentP = desiredP
        await asyncio.sleep(0.1)


async def setI():
    global desiredI, M
    M.writeRegister(15, desiredI)
    currentI = desiredI
    while True:
        if desiredI != currentI:
            M.writeRegister(16, desiredI)
            currentI = desiredI
        await asyncio.sleep(0.1)


async def websocketSender(websocket):
    global M
    while True:
        angle = M.readAngle()
        print(angle)
        await asyncio.wait_for(websocket.send(json.dumps({'angle': angle})), 1)
        await asyncio.sleep(0.1)


async def websocketReceiver(websocket):
    global desiredAngle, desiredP
    async for message in websocket:
        try:
            data = json.loads(message)
            desiredAngle = int(data['angle'])
            desiredP = int(data['P'])
        except Exception as e:
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


MODBUS_PORT = os.getenv('MODBUS_PORT', default='COM14')
# one speed unit is ~173 angle units per sec
# 360 degrees is ~4000 angle units

desiredAngle = 0
desiredP = 100
desiredI = 0

client = ModbusSerialClient(method="rtu", port=MODBUS_PORT, stopbits=1,
                            bytesize=8, parity='N', baudrate=115200,
                            timeout=0.1)
M = X3EMotor(client, 1)

M.writeRegister(16, desiredP)
M.writeRegister(15, desiredI)

startingAngle = M.readAngle()

loop = asyncio.get_event_loop()
asyncio.gather(
    websockets.serve(websocketHandler, 'localhost', 8765),
    setAngle(),
    setP(),
    setI()
)
try:
    pass
    loop.run_forever()
finally:
    M.release()
    client.close()
    loop.close()
