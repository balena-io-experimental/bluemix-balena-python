"""
IBM Bluemix Device
"""
import os
import random
import time

import psutil
import requests

###
# Get readings (output)
###
def reading_cpu(interval=0):
    """Reading CPU utilization

    Arguments:
    interval -- monitoring interval in seconds, default=0 (immediate)
    """
    return psutil.cpu_percent(interval=interval)

def reading_memory():
    """Reading amount of free memory (in bytes)
    """
    return psutil.virtual_memory().free

def reading_random(lower=0, upper=1):
    """Reading a random number from within an interval

    Arguments:
    lower -- lower bound of the interval, default=0
    upper -- upper bound of the interval, default=1
    """
    if lower > upper:
        lower, upper = upper, lower
    return random.uniform(lower, upper)

###
# Bluemix output
###
def send_readings(connection):
    """Send readings to the Bluemix platform
    """
    readings = {
        "cpu_load": reading_cpu(),
        "free_memory": reading_memory(),
        "random": reading_random()
    }
    connection.publishEvent("status", "json", readings)

###
# Handle actions (input)
###
def action_set_off():
    """Turn device off through the Supervisor API
    """
    url = "{}/v1/shutdown?apikey={}".format(os.getenv('RESIN_SUPERVISOR_ADDRESS'),
                                            os.getenv('RESIN_SUPERVISOR_API_KEY'))
    requests.post(url)

def action_set_text(text=""):
    """Print text to the log

    Arguments:
    text -- the string to display, default=""
    """
    # This could be replaced with any other kind of text display
    print("setText: {}".format(text))

def action_blink_led():
    """Blink the device identification LED (when possible) through the
    Supervisor API
    """
    url = "{}/v1/blink?apikey={}".format(os.getenv('RESIN_SUPERVISOR_ADDRESS'),
                                         os.getenv('RESIN_SUPERVISOR_API_KEY'))
    requests.post(url)

###
# Bluemix input
###
def command_callback(cmd):
    """Handle incoming commands from Bluemix
    """
    print("Command received: %s" % cmd.data)
    if cmd.command == "setOff":
        action_set_off()
    elif cmd.command == "setText":
        if 'text' not in cmd.data:
            print("Error - command is missing required information: 'text'")
        else:
            action_set_text(text)
    elif cmd.command == "blinkLed":
        action_blink_led()


# Start the monitoring service
if __name__ == "__main__":
    import ibmiotf.device

    # Authenticate
    try:
        options = {"org": os.getenv("BLUEMIX_ORG"),
                   "type": os.getenv("BLUEMIX_DEVICE_TYPE"),
                   "id": os.getenv("BLUEMIX_DEVICE_ID"),
                   "auth-method": os.getenv("BLUEMIX_AUTH_METHOD"),
                   "auth-token": os.getenv("BLUEMIX_AUTH_TOKEN")
                  }
        client = ibmiotf.device.Client(options)
    except ibmiotf.ConnectionException  as e:
        raise

    # Connect
    client.connect()

    # Handle incoming commands
    client.commandCallback = command_callback

    # Set up data loop
    try:
        READINGS_PERIOD = int(os.getenv('READINGS_PERIOD', 10))
    except ValueError:
        # By default, do a reading every 10s
        READINGS_PERIOD = 10

    # Main data loop
    i = 0
    while True:
        if i % READINGS_PERIOD == 0:
            send_readings(client)
        time.sleep(1)
