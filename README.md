# IBM Bluemix Watson IoT device on balena

Implementing a basic IBM Bluemix Watson IoT device on balena. It shows how to send data, and receive commands. Also includes an example application that can monitor the device's data and send the appropriate commands.

For detailed explamation, and setting up IBM Bluemix with balena, see the [documentation](https://balena.io/docs/learn/develop/integrations/bluemix/)!

The sensor side of the application implements 3 readings to create interesting data streams that can be used for testing:

* CPU utilization
* Free memory
* Random number

The commandss side of the application implements 3 commands:

* `setText`: set a text value, here write to the log
* `setOff`: turn the device off using the Supervisor API
* `blinkLed`: blink the device identification LED (on those devices where it is available), using the SupervisorAPI

## Device

### Auto-registering onto Bluemix

This demo includes code to use the balena the Bluemix APIs to auto-register devices onto Bluemix. For this need to create an a

* `BLUEMIX_ORG`: get it from the Watson IoT console
* `BLUEMIX_DEVICE_TYPE`: set it to the device type you created in the Watson IoT console
* `BLUEMIX_API_KEY`: create a new api key in the Watson IoT console (Access / API Keys) set the key value here
* `BLUEMIX_API_TOKEN`: the auth token part of the api access
* `RESINIO_AUTH_TOKEN`: get it from the balena dashboard / preferences

The registration process internally as follows:

1. On the start of the application, the code gets the name of the current device from the balena API, as well as a number of other information (to demonstrate setting device info).
2. It connects to the Bluemix API with the provided Bluemix API credentials, and creates a new devices with the given name and parameters.
3. When the Bluemix API returns with the new device's token, the value is set as an environment variable through the balena API.

After this, a new device should be available on the Bluemix Watson IoT console with the same name as the balena device.

### Manual device registering

After setting up your device on IBM Bluemix, and save your credentials ("organization", "device type", "device name", "authentication method", and "authentication token")) create a balena application, and define five application-wide environment variables to hold the credential values from for the devices.

* `BLUEMIX_ORG`
* `BLUEMIX_DEVICE_TYPE`
* `BLUEMIX_DEVICE_ID`
* `BLUEMIX_AUTH_METHOD`
* `BLUEMIX_DEVICE_TOKEN`
* `BLUEMIX_AUTOREGISTER`

Set `BLUEMIX_AUTOREGISTER` to `0` to disable auto-registering the device to Bluemix.

`BLUEMIX_ORG`, `BLUEMIX_DEVICE_TYPE`, and `BLUEMIX_AUTH_METHOD` will likely be the same for all devices within a balena application, so set them to the correct values. `BLUEMIX_DEVICE_ID` and `BLUEMIX_DEVICE_TOKEN` will be different for all devices, so set them application-wide to `REDEFINE` or something similar to remind you to redefine them in the device-level environmental variables!

Set up your device and connect to balena. Then in the device's dashboard, redefine the environment variables ( `BLUEMIX_DEVICE_ID` and `BLUEMIX_AUTH_TOKEN`). If you have multiple devices, repeat these steps for all.

### Other setup

For this application other optional variables.

* `READINGS_PERIOD`: how often to read the sensor values (in seconds, default is `10`)

## Application

The application is available in the `application/` directory. Copy `application.conf.sample` to `application.conf`, update the values within with the API key and other information from the Bluemix dashboard (Dashboard of your IoT platform application > Access > API Keys).

Optional: set up virtualenv:

```bash
virtualenv venv
source venv/bin/activate
```

Install required libraries:
```bash
pip install -r requirements.txt
```

Then run the application:

* `python application.py` or `python application.py --help`: show help
* `python application.py getdevices`: query registered devices
* `python application.py monitor`: stream readings from connected devices
* `python application.py settext`: send "setText" command to device
* `python application.py setoff`: send "setOff" command to device (turn off)
* `python application.py blinkled`: send "blinkLed" command to the device

## License

Copyright 2016 Rulemotion Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
