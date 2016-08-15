#!/usr/bin/env python
"""
Interact with IoT devices on IBM Bluemix
"""
import json
import os.path
import sys
import time

import click
from terminaltables import AsciiTable
import ibmiotf.application

BLUEMIX_CONFIG = "application.conf"

def myEventCallback(event):
    print("{} event '{}' received from device [{}]: {}".format(event.format,
                                                               event.event,
                                                               event.device,
                                                               json.dumps(event.data)))

def myStatusCallback(status):
    if status.action == "Disconnect":
        print("{} - device {} - {} ({})".format(status.time.isoformat(),
                                                status.device,
                                                status.action,
                                                status.reason))
    else:
        print("{} - {} - {}".format(status.time.isoformat(),
                                    status.device,
                                    status.action))

def setupClient():
    if not os.path.isfile(BLUEMIX_CONFIG):
        print("Please set up the {} configuration file!".format(BLUEMIX_CONFIG))
        sys.exit(1)
    try:
        options = ibmiotf.application.ParseConfigFile(BLUEMIX_CONFIG)
        client = ibmiotf.application.Client(options)
    except ibmiotf.ConnectionException:
        raise
    return client


@click.group()
def bluemix():
    """Interact with IoT devices on IBM Bluemix
    """
    pass

@bluemix.command()
@click.option('--devtype', default=None, help='The deviceType to send the command to (optional)')
def monitor(devtype):
    """Stream data from all devices/one type
    """
    client = setupClient()
    client.deviceStatusCallback = myStatusCallback
    client.deviceEventCallback = myEventCallback
    client.connect()
    if devtype:
        client.subscribeToDeviceStatus(deviceType=devtype)
        client.subscribeToDeviceEvents(deviceType=devtype)
    else:
        client.subscribeToDeviceStatus()
        client.subscribeToDeviceEvents()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            client.disconnect()
            sys.exit()

@bluemix.command()
def getdevices():
    """Query registered devices
    """
    client = setupClient()
    devices = client.api.getDevices()
    print("Total devices: {}".format(devices['meta']['total_rows']))
    if devices['meta']['total_rows'] > 0:
        table_data = [["Device Type", "Device ID"]]
        for result in devices['results']:
            table_data += [[result['typeId'], result['deviceId']]]
        table = AsciiTable(table_data)
        print(table.table)

@bluemix.command()
@click.option('--devtype', prompt='Device type', help='The deviceType to send the command to.')
@click.option('--devid', prompt='Device id', help='The deviceId to send the command to.')
@click.option('--text', prompt='Text to send', help='Text to send to device/devices')
def settext(devtype, devid, text):
    """Send "setText" command to device
    """
    client = setupClient()
    client.connect()
    on_publish = lambda: sys.stdout.write("Command: setText sent: {}\n".format(text))
    client.publishCommand(deviceType=devtype,
                          deviceId=devid,
                          command="setText",
                          msgFormat="json",
                          data={"text": text},
                          qos=0,
                          on_publish=on_publish)
    client.disconnect()

@bluemix.command()
@click.option('--devtype', prompt='Device type', help='The deviceType to send the command to.')
@click.option('--devid', prompt='Device id', help='The deviceId to send the command to.')
def blinkLed(devtype, devid):
    """Send "blinkLed" command to device
    """
    client = setupClient()
    client.connect()
    on_publish = lambda: sys.stdout.write("Command: blinkLed sent\n")
    client.publishCommand(deviceType=devtype,
                          deviceId=devid,
                          command="blinkLed",
                          msgFormat="json",
                          data=None,
                          qos=0,
                          on_publish=on_publish)
    client.disconnect()

@bluemix.command()
@click.option('--devtype', prompt='Device type', help='The deviceType to send the command to.')
@click.option('--devid', prompt='Device id', help='The deviceId to send the command to.')
def setoff(devtype, devid):
    """Send "setOff" command to device (turn off)
    """
    click.confirm('Are you sure you want to turn the device off?', abort=True)
    client = setupClient()
    client.connect()
    on_publish = lambda: sys.stdout.write("Command: setOff sent\n")
    client.publishCommand(deviceType=devtype,
                          deviceId=devid,
                          command="setOff",
                          msgFormat="json",
                          data=None,
                          qos=0,
                          on_publish=on_publish)
    client.disconnect()

if __name__ == "__main__":
    bluemix()
