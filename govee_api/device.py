import govee_api.api as gapi
import abc
import colour
import math

class GoveeDevice(abc.ABC):
    """ Govee Smart device """
    
    def __init__(self, govee, identifier, topic, sku, name, connected):
        """ Creates a new Govee device """

        super(GoveeDevice, self).__init__()

        self.__govee = govee
        self.__identifier = identifier
        self.__topic = topic
        self.__sku = sku
        self.__name = name
        self.__connected = connected

    @property
    def identifier(self):
        """ Gets the device identifier """

        return self.__identifier

    @property
    def _topic(self):
        """ Gets the device topic """

        return self.__topic

    @property
    def sku(self):
        """ Gets the device SKU """

        return self.__sku

    @property
    def name(self):
        """ Gets the device name """

        if not self.__name: # Should never happen, but..
            return '<no name> {} @ {}'.format(self.__sku, self.__identifier)
        else:
            return self.__name

    @name.setter
    def _name(self, val):
        """ Sets the device name """

        self.__name = val

    @property
    @abc.abstractmethod
    def friendly_name(self):
        """ Gets the devices' friendly name """

        pass

    @property
    def connected(self):
        """ Gets if the device is connected with the Cloud """

        return self.__connected

    @abc.abstractmethod
    def request_status(self):
        """ Request device status """

        pass    

    def _update_state(self, state):
        """ Update device state """

        conn = state['connected']
        if isinstance(conn, bool):
            self.__connected = conn
        elif conn == 'true':
            self.__connected = True
        elif conn == 'false':
            self.__connected = False
        else:
            self.__connected = None

    def _publish_command(self, command, data):
        """ Build command to control Govee Smart device """

        self.__govee._publish_payload(self, command, data)


class ToggleableGoveeDevice(GoveeDevice):
    """ Toggleable Govee Smart device """
    
    def __init__(self, govee, identifier, topic, sku, name, connected):
        """ Creates a new toggleable Govee device """

        super(ToggleableGoveeDevice, self).__init__(govee, identifier, topic, sku, name, connected)

        self.__on = None
    
    @property
    def on(self):
        """ Gets if the device is on or off """

        return self.__on

    @on.setter
    def on(self, val):
        """ Turns the device on or off """

        self.__turn(val)

    def toggle(self):
        """ Toggles the device status """

        self.__turn(not self.on)

    def __turn(self, val):
        """ Turn the device on or off """

        if val != self.__on:
            self._publish_command('turn', {
                'val': val
            })

    def _update_state(self, state):
        """ Update device state """

        super(ToggleableGoveeDevice, self)._update_state(state)

        self.__on = state['onOff'] == 1


class GoveeLight(ToggleableGoveeDevice):
    """ Represents a Govee light of any type """

    def __init__(self, govee, identifier, topic, sku, name, connected):
        """ Creates a new abstract Govee light device """

        super(GoveeLight, self).__init__(govee, identifier, topic, sku, name, connected)

        self.__brightness = None

    def __calc_brightness(self, brightness):
        val = 0
        if brightness:
            val = max(min(int(round(brightness * 255)), 255), 0)
        return val

    @property
    def brightness(self):
        """ Gets the light brightness  """

        return self.__brightness

    @brightness.setter
    def brightness(self, val):
        """ Sets the light brightness """

        if val != self.__brightness:
            self._publish_command('brightness', {
                'val': self.__calc_brightness(val)
            })

    def request_status(self):
        """ Request device status """

        # I have found out that I can fetch the status of the devices by sending an empty
        # (=no data) `turn` command to them. I do not know how the official app does it and
        # I don't want to decompile it for legal reasons.

        self._publish_command('turn', {})

    def _update_state(self, state):
        """ Update device state """

        super(GoveeLight, self)._update_state(state)

        self.__brightness = max(min(state['brightness'] / 255, 1.0), 0.0)


class GoveeRgbLight(GoveeLight):
    """ Represents a Govee RGB light of any type """

    def __init__(self, govee, identifier, topic, sku, name, connected):
        """ Creates a new abstract Govee RGB light device """

        super(GoveeRgbLight, self).__init__(govee, identifier, topic, sku, name, connected)

        self.__color = None
        self.__color_temperature = None

    def __fix_color_temperature(self, color_temperature):
        fixed = 0
        if color_temperature:
            fixed = max(min(color_temperature, 9000), 2000)
        return fixed

    @property
    def color(self):
        """ Gets the light color  """

        return self.__color

    @color.setter
    def color(self, val):
        """ Sets the light color """

        if val:
            red, green, blue = self._calc_color(val)

            self._publish_command('color', {
                'red': red,
                'green': green,
                'blue': blue
            })

    def _calc_color(self, val):
        red = 0
        green = 0
        blue = 0

        if isinstance(val, colour.Color):
            if val == self.__color:
                return
            red = int(round(val.red * 255))
            green = int(round(val.green * 255))
            blue = int(round(val.blue * 255))
        elif isinstance(val, tuple) and len(val) == 3:
            if int(round(self.__color.red * 255)) == val[0] and \
               int(round(self.__color.get_green * 255)) == val[1] and \
               int(round(self.__color.blue * 255)) == val[20]:
                return
            red = val[0]
            green = val[1]
            blue = val[2]
        else:
            raise gapi.GoveeException('Invalid color value provided')
        
        return (red, green, blue)

    @property
    def color_temperature(self):
        """ Gets the light's color temperature  """

        return self.__color_temperature

    @color_temperature.setter
    def color_temperature(self, val):
        """ Sets the light's color temperature """

        color_temp = self.__fix_color_temperature(val)
        if color_temp > 0 and color_temp != self.__color_temperature:
            self._publish_command('colorTem', {
                'color': self.__kelvin_to_color(color_temp),
                'colorTemInKelvin': color_temp
            })

    def __kelvin_to_color(self, color_temperature):
        """ Calculate RGB color based on color temperature """

        """
        This code is based on a algorithm published by Tanner Helland on
        https://tannerhelland.com/2012/09/18/convert-temperature-rgb-algorithm-code.html
        """

        # Minimum temperature is 1000, maximum temperature is 40000
        color_temp = min(max(color_temperature, 1000), 40000) / 100

        # Calculate red
        if color_temp <= 66:
            red = 255
        else:
            red = min(max(329.698727446 * pow(color_temp - 60, -0.1332047592), 0), 255)
        
        # Calculate green
        if color_temp <= 66:
            green = min(max(99.4708025861 * math.log(color_temp) - 161.1195681661, 0), 255)
        else:
            green = min(max(288.1221695283 * pow(color_temp - 60, -0.0755148492), 0), 255)

        # Calculate blue
        if color_temp >= 66:
            blue = 255
        elif color_temp <= 19:
            blue = 0
        else:
            blue = min(max(138.5177312231 * math.log(color_temp - 10) - 305.0447927307, 0), 255)

        return {
            'red': int(round(red)),
            'green': int(round(green)),
            'blue': int(round(blue))
        }

    def _update_state(self, state):
        """ Update device state """

        super(GoveeRgbLight, self)._update_state(state)

        if 'colorTemInKelvin' in state.keys():
            self.__color_temperature = self.__fix_color_temperature(state['colorTemInKelvin'])
        else:
            self.__color_temperature = None

        if 'color' in state.keys():
            color = state['color']
            self.__color = colour.Color(rgb = (color['r'] / 255.0, color['g'] / 255.0, color['b'] / 255.0))
        else:
            self.__color = None


class GoveeWhiteBulb(GoveeLight):
    """ Represents a Govee bulb """

    def __init__(self, govee, identifier, topic, sku, name, connected):
        """ Creates a new Govee white bulb device """

        super(GoveeWhiteBulb, self).__init__(govee, identifier, topic, sku, name, connected)

    @property
    def friendly_name(self):
        """ Gets the devices' friendly name """

        return 'White bulb'


class GoveeBulb(GoveeRgbLight):
    """ Represents a Govee RGB bulb """

    def __init__(self, govee, identifier, topic, sku, name, connected):
        """ Creates a new Govee RGB bulb device """

        super(GoveeBulb, self).__init__(govee, identifier, topic, sku, name, connected)

    @property
    def friendly_name(self):
        """ Gets the devices' friendly name """

        return 'RGB bulb'

class GoveeLedStrip(GoveeRgbLight):
    """ Represents a Govee LED strip """

    def __init__(self, govee, identifier, topic, sku, name, connected):
        """ Creates a new Govee LED strip device """

        super(GoveeLedStrip, self).__init__(govee, identifier, topic, sku, name, connected)

    @property
    def friendly_name(self):
        """ Gets the devices' friendly name """

        return 'RGB LED strip'