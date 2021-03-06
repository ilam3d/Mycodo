# coding=utf-8
import logging
import time

# Input information
INPUT_INFORMATION = {
    'input_name_unique': 'MCP342x',
    'input_manufacturer': 'Microchip',
    'input_name': 'MCP342x',
    'measurements_name': 'Voltage (Analog-to-Digital Converter)',
    'measurements_list': ['voltage'],
    'options_enabled': ['adc_channel', 'adc_gain', 'adc_options', 'period', 'pre_output'],
    'options_disabled': ['interface', 'i2c_location'],

    'dependencies_module': [
        ('pip-pypi', 'smbus2', 'smbus2'),
        ('pip-pypi', 'MCP342x', 'MCP342x==0.3.3')
    ],
    'interfaces': ['I2C'],
    'i2c_location': [
        '0x68',
        '0x6A',
        '0x6C',
        '0x6E',
        '0x6F'
    ],
    'i2c_address_editable': False,
    'analog_to_digital_converter': True,
    'adc_channel': [
        (0, 'Channel 0'),
        (1, 'Channel 1'),
        (2, 'Channel 2'),
        (3, 'Channel 3')
    ],
    'adc_gain': [
        (1, '1'),
        (2, '2'),
        (4, '4'),
        (8, '8')
    ],
    'adc_volts_min': -4.096,
    'adc_volts_max': 4.096
}


class ADCModule(object):
    """ ADC Read """
    def __init__(self, input_dev, testing=False):
        self.logger = logging.getLogger('mycodo.mcp342x')
        self.acquiring_measurement = False
        self._voltage = None

        self.i2c_address = int(str(input_dev.location), 16)
        self.i2c_bus = input_dev.i2c_bus
        self.adc_channel = input_dev.adc_channel
        self.adc_gain = input_dev.adc_gain
        self.adc_resolution = input_dev.adc_resolution

        if not testing:
            from smbus2 import SMBus
            from MCP342x import MCP342x
            self.logger = logging.getLogger(
                'mycodo.mcp342x_{id}'.format(id=input_dev.unique_id.split('-')[0]))
            self.bus = SMBus(self.i2c_bus)
            self.adc = MCP342x(self.bus,
                               self.i2c_address,
                               channel=self.adc_channel,
                               gain=self.adc_gain,
                               resolution=self.adc_resolution)

    def __iter__(self):
        """
        Support the iterator protocol.
        """
        return self

    def next(self):
        """
        Call the read method and return voltage information.
        """
        if self.read():
            return None
        return dict(voltage=float('{0:.4f}'.format(self._voltage)))

    @property
    def voltage(self):
        return self._voltage

    def get_measurement(self):
        self._voltage = None
        voltage = self.adc.convert_and_read()
        return voltage

    def read(self):
        """
        Takes a reading

        :returns: None on success or 1 on error
        """
        if self.acquiring_measurement:
            self.logger.error("Attempting to acquire a measurement when a"
                              " measurement is already being acquired.")
            return 1
        try:
            self.acquiring_measurement = True
            self._voltage = self.get_measurement()
            if self._voltage is not None:
                return  # success - no errors
        except Exception as e:
            self.logger.error(
                "{cls} raised an exception when taking a reading: "
                "{err}".format(cls=type(self).__name__, err=e))
        finally:
            self.acquiring_measurement = False
        return 1


if __name__ == "__main__":
    class Data:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    input_dev = Data(id='00001',
                     unique_id='asdf-ghjk',
                     location='0x68',
                     i2c_bus=1,
                     adc_channel=0,
                     adc_gain=1,
                     adc_resolution=12)

    mcp = ADCModule(input_dev)

    while 1:
        mcp.read()
        print("Voltage: {}".format(mcp.voltage))
        time.sleep(1)
