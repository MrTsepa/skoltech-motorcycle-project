from pymodbus.exceptions import ModbusIOException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian


class X3EMotor:
    MODE_ANGLE = 1
    MODE_SPEED = 2
    MODE_PWM = 3
    MODE_NONE = 0

    def __init__(self, client, id, mode=MODE_NONE):
        self._mode = self.MODE_NONE
        self.client = client
        self.id = id
        self.mode = mode

        self.angle = 0
        self.speed = 0
        super(X3EMotor, self).__init__()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if self._mode != value:
            self._mode = self.MODE_NONE  # THIS IS VERY IMPORTANT
            self.updateMode()
        self._mode = value
        self.updateMode()

    def setMode(self, mode):
        self.mode = mode

    def setAngle(self, angle):
        if self.mode != self.MODE_ANGLE:
            self.mode = self.MODE_ANGLE
        self.angle = int(angle)
        self.updateData()

    def setSpeed(self, speed):
        if self.mode != self.MODE_SPEED:
            self.mode = self.MODE_SPEED
        self.speed = int(speed)
        self.updateData()

    def release(self):
        self.mode = self.MODE_NONE

    def readAngle(self):
        result = self.client.read_holding_registers(67, 2, unit=self.id)
        if isinstance(result, ModbusIOException):
            raise result
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)
        return decoder.decode_32bit_int()

    def readRegister(self, reg, bit=16):
        result = self.client.read_holding_registers(reg, 2, unit=self.id)
        if isinstance(result, ModbusIOException):
            raise result
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)
        return decoder.decode_16bit_int() if bit == 16 else decoder.decode_32bit_int()

    def writeRegister(self, reg, data):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        builder.add_16bit_int(data)
        payload = builder.to_registers()[0]
        self.client.write_register(reg, payload, unit=self.id)

    def updateMode(self):
        self.client.write_register(0, self.mode, unit=self.id)

    def updateData(self):
        if self.mode == self.MODE_ANGLE:
            builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                           wordorder=Endian.Little)
            builder.add_16bit_int(self.angle)
            payload = builder.to_registers()
            self.client.write_register(4, payload[0], unit=self.id)
        elif self.mode == self.MODE_SPEED:
            builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                           wordorder=Endian.Little)
            builder.add_16bit_int(self.speed)
            payload = builder.to_registers()[0]
            self.client.write_register(3, payload, unit=self.id)

    def setID(self, index):
        self.client.write_register(129, index, unit=self.id)

    def save2flash(self):
        self.client.write_register(130, 0, unit=self.id)

    def setAngle_PID_P(self, i):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        builder.add_16bit_int(i)
        payload = builder.to_registers()[0]
        self.client.write_register(16, payload, unit=self.id)

    def setAngle_PID_D(self, i):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        builder.add_16bit_int(i)
        payload = builder.to_registers()[0]
        self.client.write_register(17, payload, unit=self.id)

    def setSpeed_PID_P(self, i):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        builder.add_16bit_int(i)
        payload = builder.to_registers()[0]
        self.client.write_register(13, payload, unit=self.id)

    def setSpeed_PID_D(self, i):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        builder.add_16bit_int(i)
        payload = builder.to_registers()[0]
        self.client.write_register(14, payload, unit=self.id)