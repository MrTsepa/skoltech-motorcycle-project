import asyncio

from x3emotor import X3EMotor


class MotorAsyncController:
    def __init__(self, motor: X3EMotor, desiredP=100, desiredI=0):
        self.motor = motor
        self.startingAngle = motor.readAngle()
        self.desiredAngle = self.startingAngle
        self.desiredP = desiredP
        self.desiredI = desiredI

    async def angleTask(self, max_speed=20):
        while True:
            print(self.motor.id, "New desired angle:", self.desiredAngle)
            prevDesiredAngle = self.desiredAngle
            finished = False
            while self.desiredAngle == prevDesiredAngle:
                currentAngle = self.motor.readAngle()
                dist = abs(currentAngle - self.desiredAngle)
                if finished:
                    pass
                elif dist < 500:
                    self.motor.setAngle(self.desiredAngle)
                    finished = True
                elif dist < max_speed * 30:
                    self.motor.setSpeed(-5 if self.desiredAngle < currentAngle else 5)
                else:
                    self.motor.setSpeed(-max_speed if self.desiredAngle < currentAngle else max_speed)
                await asyncio.sleep(0.01)

    async def pTask(self):
        self.motor.writeRegister(16, self.desiredP)
        currentP = self.desiredP
        while True:
            if self.desiredP != currentP:
                print(self.motor.id, "New desired P:", self.desiredP)
                self.motor.writeRegister(16, self.desiredP)
                currentP = self.desiredP
            await asyncio.sleep(0.1)

    async def iTask(self):
        self.motor.writeRegister(15, self.desiredI)
        currentI = self.desiredI
        while True:
            if self.desiredI != currentI:
                self.motor.writeRegister(16, self.desiredI)
                currentI = self.desiredI
            await asyncio.sleep(0.1)