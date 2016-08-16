"""
Glue for IBM Bluemix IoT and resin.io
"""
import os

from resin import Resin
import ibmiotf.application

def register(resinio_auth_token):
    """Register a device to IBM Bluemix

    Input:
    resinio_auth_token: authentication token from the user dashboard/preferences

    Output:
    device_id: the device id, new if just registered, existing if already has such device
    device_token: authentication token, new if just registered, from env vars if exists
    """
    resin = Resin()
    uuid = os.getenv("RESIN_DEVICE_UUID")
    resin.auth.login_with_token(resinio_auth_token)
    device = resin.models.device.get(uuid)

    # Information to add to Bluemix about the device
    device_id = device["name"]
    machine = device["device_type"]
    resinos = device["os_version"]
    location = device["location"]

    # Device registration data
    device_type_id = os.getenv("BLUEMIX_DEVICE_TYPE")
    device_info = {"model": machine,
                   "fwVersion": resinos,
                   "descriptiveLocation": location
                  }
    # Bluemx API login
    try:
        service_options = {"org": os.getenv("BLUEMIX_ORG"),
                           "id": "DeviceRegistration",
                           "auth-method": "apikey",
                           "auth-key": os.getenv("BLUEMIX_API_KEY"),
                           "auth-token": os.getenv("BLUEMIX_API_TOKEN")
                          }
        service = ibmiotf.application.Client(service_options)
    except ibmiotf.ConnectionException:
        raise

    # Device registration and environmental setup
    try:
        r = service.api.registerDevice(typeId=device_type_id, deviceId=device_id, deviceInfo=device_info)
        device_token = r["authToken"]

        create_or_update_env(resin, uuid, "BLUEMIX_DEVICE_ID", device_id)
        create_or_update_env(resin, uuid, "BLUEMIX_DEVICE_TOKEN", device_token)
    except ibmiotf.APIException as e:
        if e.httpCode == 403:
            print("Device '{}' is already registered".format(device_id))
            device_token = os.getenv("BLUEMIX_DEVICE_TOKEN")
        else:
            raise
    return device_id, device_token

def create_or_update_env(resinapi, uuid, name, value):
    """Check if a given device environmental variable already exists for this device,
    if it does, update it with 'value', otherwise create it

    Input:
    resinapi: authenticated resin connection
    uuid: device UUID
    name: variable name
    value: variable value to set or update to
    """
    if os.getenv(name, None):
        envvars = resinapi.models.environment_variables.device.get_all(uuid)
        for envvar in envvars:
            if envvar["env_var_name"] == name:
                resinapi.models.environment_variables.device.update(envvar["id"], value)
                break
    else:
        resinapi.models.environment_variables.device.create(uuid, name, value)
