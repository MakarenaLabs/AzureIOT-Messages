# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient
#from xnucleo_module.main import getSensorsOneShot as gsos
import json
import time
import requests

with open('azure_config.json', 'r') as az_conf:
	azure_config = json.load(az_conf)


IOTHUB_DEVICE_CONNECTION_STRING = azure_config["connection_string"]


#IOTHUB_DEVICE_CONNECTION_STRING = 'HostName=Z7010.azure-devices.net;DeviceId=Z7010-board1;SharedAccessKey=tSZ5eYqdBjSGMnhcPQsJqJaPxyuQ1TCJYvAPveN3iVg='

configs = {}

configs["config"] = {}
configs["sensors"] = {}
configs["relays"] = {}

configs["config"]["frequency"] = 5
configs["config"]["updated"] = 0

configs["sensors"]['hum'] = 30
configs["sensors"]['temp1'] = 26
configs["sensors"]['pressure'] = 1000
configs["sensors"]['temp2'] = 26.5
configs["sensors"]['accel1'] = 9.8
configs["sensors"]['Gaxis'] = 12
configs["sensors"]['accel2'] = 2.34
configs["sensors"]['magneto'] = 11

configs["relays"]['relay1'] = False
configs["relays"]['relay2'] = False
configs["relays"]['relay3'] = False
configs["relays"]['relay4'] = False


async def main():
    while True:
        # Fetch the connection string from an enviornment variable

        # = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
        conn_str = IOTHUB_DEVICE_CONNECTION_STRING

        # Create instance of the device client using the connection string
        device_client = IoTHubDeviceClient.create_from_connection_string(
            conn_str)

        # Connect the device client.
        await device_client.connect()

        # Send a single message
        print("Sending message...")

        # Get sensors informations
        #j = gsos(3)
        r = requests.get("http://localhost:5000/devices")
        j = r.json()

        # Read configs (frequency updates, relay [1-4] status)
        try:
            with open('../microserver-flask/data.json') as json_file:
                configs = json.load(json_file)
        except Exception as e:
            print(e)

        # join sensors informations with read configuration
        #j = json.loads(j)
        #j.update(configs)

        j["relay1"] = configs["relays"]["relay1"]
        j["relay2"] = configs["relays"]["relay2"]
        j["relay3"] = configs["relays"]["relay3"]
        j["relay4"] = configs["relays"]["relay4"]
        j["frequency"] = configs["config"]["frequency"]
        j["updated"] = configs["config"]["updated"]

        #with open('data.json', 'w') as outfile:
        #    json.dump(j, outfile)

        # printing the message preview
        print("Sending message: {}".format(j))
        # wait for client and send Azure IOT message
        await device_client.send_message(json.dumps(j))
        print("Message successfully sent!")

        # If dashboard is in "update" status save it as False
        if configs["config"]['updated']:
            configs["config"]['updated'] = 0
            with open('../microserver-flask/data.json', 'w') as outfile:
                json.dump(configs, outfile)

        # finally, disconnect
        await device_client.disconnect()
        time.sleep(configs["config"]['frequency'])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
