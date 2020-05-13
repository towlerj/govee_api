=====
Usage
=====

To use Govee API in a project::

    from govee_api import api, device
    import time
    import colour

    def main():
        # Create Govee client and configure event handlers
        govee_cli = api.Govee('your_email', 'your_password', 'your_client_id_or_EMPTY')
        # BEWARE: This will create a new Govee Client ID with every login. It is recommended to provide an existing client ID
        # within the `Govee` contructor. You can fetch your generated client ID via `govee.client_id` after your successful login

        # Event raised when a new device is discovered
        govee_cli.on_new_device = _on_new_device

        # Event raised when a device status was updated
        govee_cli.on_device_update = _on_device_update

        # Login to Govee
        govee_cli.login()

        # Print out the used client ID
        print('Current client ID is: {}'.format(govee_cli.client_id))

        # Fetch known devices from server
        govee_cli.update_device_list()

        print('Preparing for action :-)')
        # Don't do this in real life. Use the callbacks the client provides to you!
        time.sleep(10)

        # Loop over all devices
        for dev in govee_cli.devices.values():
            if dev.connected:
                print('Fun with device {} ...'.format(dev.name))

                # Turn on device
                dev.on = True

                # Wait a second
                time.sleep(1)

                # Save initial brightness
                brightness_backup = dev.brightness

                # Set brightness to 50%
                dev.brightness = 0.5

                # Wait a second
                time.sleep(1)

                # Set brightness to 100%
                dev.brightness = 1.0

                # Wait a second
                time.sleep(1)

                if isinstance(dev, device.GoveeRgbLight):
                    # Save initial color
                    color_backup = dev.color

                    # Set color temperature to 2100 kelvin (warm white)
                    dev.color_temperature = 2100

                    # Wait a second
                    time.sleep(1)

                    # Set color to green
                    dev.color = colour.Color('green')

                    # Wait a second
                    time.sleep(1)

                    # Set color to red
                    dev.color = (255, 0, 0)

                    # Wait a second
                    time.sleep(1)

                    # Set color to dodgerblue
                    dev.color = colour.Color('dodgerblue')

                    # Wait a second
                    time.sleep(1)

                    # Restore color
                    if color_backup:
                        dev.color = color_backup

                # Wait a second
                time.sleep(1)

                # Restore initial brightness
                dev.brightness = brightness_backup

                # Wait a second
                time.sleep(1)

                # Turn the device off
                dev.on = False
            else:
                print('Device {} is not connected. Skipping...'.format(dev.name))

        print('All done!')


    # Event handlers
    def _on_new_device(govee_cli, dev, raw_data):
        """ New device event """

        connected_str = _get_connected_str(dev.connected)
        print('NEW DEVICE [{}][{} {}] {} -> Connected: {}'.format(dev.identifier, dev.sku, dev.friendly_name, dev.name, \
            connected_str))

    def _on_device_update(govee_cli, dev, old_dev, raw_data):
        """ Device update event """

        connected_str = _get_connected_str(dev.connected)
        on_str = 'No'
        if dev.on:
            on_str = 'Yes'

        if isinstance(dev, device.GoveeRgbLight):
            color_str = 'Non-RGB'
            if dev.color:
                color_str = dev.color.hex_l
            elif dev.color_temperature and dev.color_temperature > 0:
                color_str = '{} Kelvin'.format(dev.color_temperature)
            print('DEVICE UPDATE [{}][{} {}] {} -> Connected: {}, On: {}, Brightness: {}, Color: {}'.format(dev.identifier, \
                dev.sku, dev.friendly_name, dev.name, connected_str, on_str, dev.brightness, color_str))
        else:
            print('DEVICE UPDATE [{}][{} {}] {} -> Connected: {}, On: {}, Brightness: {}'.format(dev.identifier, dev.sku, \
                dev.friendly_name, dev.name, connected_str, on_str, dev.brightness))


    # Helper
    def _get_connected_str(connected):
        """ Get connection status string """

        connected_str = 'No'
        if connected:
            connected_str = 'Yes'
        elif connected is None:
            connected_str = '???'
        return connected_str


    if __name__ == '__main__':
        main()