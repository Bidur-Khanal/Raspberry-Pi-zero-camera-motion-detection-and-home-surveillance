import smbus

class I2C:
    def __init__(self):
        self.bus = smbus.SMBus(1)

    def read_operation(self,Device_address):
        DEVICE_ADDRESS = Device_address     #7 bit address (will be left shifted to add the read write bit)
        #DEVICE_REG_MODE1 = 0x00
        #DEVICE_REG_LEDOUT0 = 0x1d

        #read from the device
        y=self.bus.read_byte_data(Device_address,0xFB)
        print y
    def write_operation(self):
        #Write a single register
        self.bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0x80)

        #Write an array of registers
        ledout_values = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
        self.bus.write_i2c_block_data(DEVICE_ADDRESS, DEVICE_REG_LEDOUT0, ledout_values)
        
i= I2C()
i.read_operation(0x76)
