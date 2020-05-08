import sys
import click
import configparser
import time
import colour
import govee

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--config', '-c', type=click.File('r+'),
              required=True,
              help='Config file with Govee Home credentials')
def main(config=None):
    # Read config file
    cfg = configparser.ConfigParser()
    cfg.read_file(config)

    click.echo('# Using Govee login {}...'.format(cfg['login']['email']))

    # Create Govee client and configure event handlers
    govee_cli = govee.Govee(cfg['login']['email'], cfg['login']['passwd'])
    govee_cli.on_new_device = _on_new_device
    govee_cli.on_device_update = _on_device_update

    # Login to Govee
    govee_cli.login()

    # Get device list
    click.echo('# Fetching device list...')
    govee_cli.update_device_list()
    click.echo('# Done. Waiting for device updates...')

    # Update device
    """
    time.sleep(2)
    devices = govee_cli.devices
    print(len(devices))
    device = govee_cli.devices['XX:XX:XX:XX:XX']
    print(device)
    device.brightness = 255
    time.sleep(1)
    color = colour.Color('red')
    device.color = color
    while color.get_red() > 0:
        time.sleep(0.5)
        color.set_red(color.get_red() - 0.01)
        color.set_blue(min(color.get_blue() + 0.03, 1))
        device.color = color
    """

    while True:
        time.sleep(1)

    return 0

def _get_connected_str(connected):
    connected_str = 'No'
    if connected:
        connected_str = 'Yes'
    elif connected is None:
        connected_str = '???'
    return connected_str

def _on_new_device(govee_cli, device):
    connected_str = _get_connected_str(device.connected)
    print('NEW DEVICE [{}][{}] {} -> Connected: {}'.format(device.identifier, device.sku, device.name, connected_str))

def _on_device_update(govee_cli, device):
    # Currently only lights are supported. Thus, every device is of type `AbstractGoveeRgbLight`
    connected_str = _get_connected_str(device.connected)
    on_str = 'No'
    if device.on:
        on_str = 'Yes'
    color_str = 'Non-RGB'
    if device.color:
        color_str = device.color.hex_l
    print('DEVICE UPDATE [{}][{}] {} -> Connected: {}, On: {}, Brightness: {}, Color: {}'.format(device.identifier, \
        device.sku, device.name, connected_str, on_str, device.brightness, color_str))


if __name__ == "__main__":
    main()