import threading
import time
import json
import requests
from azure.iot.device import IoTHubDeviceClient

with open('azure_config.json', 'r') as az_conf:
	azure_config = json.load(az_conf)


CONNECTION_STRING = azure_config["connection_string"]
# Setted connection string
#CONNECTION_STRING = "HostName=Z7010.azure-devices.net;DeviceId=Z7010-board1;SharedAccessKey=tSZ5eYqdBjSGMnhcPQsJqJaPxyuQ1TCJYvAPveN3iVg="
FLASK_ENDPOINT = "http://localhost:5000/devices"
last_data = {}

data_path = "../microserver-flask/data.json"

def setRelay(relay, enabled):
    # Call Relay function in modbus_master_relay to set a specific status
    try:
        modbus_relay.set_relay_function(relay, enabled)
        time.sleep(0.05)
    except Exception as e:
        pass


def message_listener(client):
    # Listener for incoming messages from AzureIOT
    global last_data
    while True:
        # Receive a message
        message = client.receive_message()

        # Read the message as JSON object
        data = json.loads(message.data)
        last_data = data

        # Read relay status and set it
        #setRelay(0, data["relay1"])
        #setRelay(1, data["relay2"])
        #setRelay(2, data["relay3"])
        #setRelay(3, data["relay4"])

        headers = {'content-type': 'application/json'}
        r = requests.post(FLASK_ENDPOINT, data=message.data, headers=headers)

        print("\nMessage received: {}".format(data))

        with open(data_path, 'r') as json_file:
            new_local_data = json.load(json_file)

        new_local_data['config']['updated'] = 1

        print("UPDATED")
        print(new_local_data)

        # Save the message as file
        with open(data_path, 'w') as outfile:
            json.dump(new_local_data, outfile)


def iothub_client_run():
    # Main thread
    try:
        # Initializing client from CONNECTION_STRING
        client = IoTHubDeviceClient.create_from_connection_string(
            CONNECTION_STRING)

        # Creating a new thread with message_listener as target
        message_listener_thread = threading.Thread(
            target=message_listener, args=(client,))

        # Set the thread as daemon
        message_listener_thread.daemon = True

        # Start the thread
        message_listener_thread.start()

        while True:
            time.sleep(1000)

    except KeyboardInterrupt:
        print ("IoT Hub C2D Messaging device stopped")


def offline_updater():

    threading.Timer(1, offline_updater).start()
    
    print("LAST_DATA:")
    print(last_data)

    with open(data_path, 'r') as json_file:
        new_local_data = json.load(json_file)

    new_data = {
        "frequency": new_local_data["config"]["frequency"],
        "updated": new_local_data["config"]["updated"],
        "hum": new_local_data["sensors"]["hum"],
        "temp1": new_local_data["sensors"]["temp1"],
        "pressure": new_local_data["sensors"]["pressure"],
        "temp2": new_local_data["sensors"]["temp2"],
        "accel1": new_local_data["sensors"]["accel1"],
        "Gaxis": new_local_data["sensors"]["Gaxis"],
        "accel2": new_local_data["sensors"]["accel2"],
        "magneto": new_local_data["sensors"]["magneto"],
        "relay1": new_local_data["relays"]["relay1"],
        "relay2": new_local_data["relays"]["relay2"],
        "relay3": new_local_data["relays"]["relay3"],
        "relay4": new_local_data["relays"]["relay4"],
    }

    #{'frequency': 1, 'relay1': True, 'relay2': True, 'relay3': False, 'relay4': False}

    modrelays = {}
    modrelays["frequency"] = new_data["frequency"]
    modrelays["relay1"] = new_data["relay1"]
    modrelays["relay2"] = new_data["relay2"]
    modrelays["relay3"] = new_data["relay3"]
    modrelays["relay4"] = new_data["relay4"]

    print("NEW_DATA:")
    print(new_data)

    if modrelays != last_data:
        print("CHANGED")
        headers = {'content-type': 'application/json'}
        r = requests.post("http://localhost:3000/offline_update", data=json.dumps(new_data), headers=headers)


if __name__ == '__main__':
    print ("Starting the Python IoT Hub C2D Messaging device...")
    print ("Waiting for C2D messages, press Ctrl-C to exit")

    with open('../microserver-flask/data.json', 'r') as json_file:
        local_data = json.load(json_file)

    last_data = {
        "frequency": local_data["config"]["frequency"],
        #"updated": local_data["config"]["updated"],
        #"hum": local_data["sensors"]["hum"],
        #"temp1": local_data["sensors"]["temp1"],
        #"pressure": local_data["sensors"]["pressure"],
        #"temp2": local_data["sensors"]["temp2"],
        #"accel1": local_data["sensors"]["accel1"],
        #"Gaxis": local_data["sensors"]["Gaxis"],
        #"accel2": local_data["sensors"]["accel2"],
        #"magneto": local_data["sensors"]["magneto"],
        "relay1": local_data["relays"]["relay1"],
        "relay2": local_data["relays"]["relay2"],
        "relay3": local_data["relays"]["relay3"],
        "relay4": local_data["relays"]["relay4"],
    }

    offline_updater()
    iothub_client_run()
