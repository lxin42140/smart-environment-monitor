import threading
import time
import random
import requests
import json
from db.db_helper import DBHelper
from hub import Hub
import paho.mqtt.client as mqtt

############################ START OF HUB ############################
HEADERS = {'content-type': 'application/json'}
BASE_URI = "http://172.20.10.2:23336"  # macBook air hotspot
CLOUD_SENSOR_DATE_URI = BASE_URI + "/sensor-data"

hub = Hub(hub_identifier="lixin-fog", connect_radio=True)


def toggle_fog_led():
    while True:
        # on off green
        if hub.green_led_on:
            hub.toggle_fog_led(hub.ledGreenPin, on=True)
        else:
            hub.toggle_fog_led(hub.ledGreenPin, on=False)

        # on off red
        if hub.red_led_on:
            hub.toggle_fog_led(hub.ledRedPin, on=True)
        else:
            hub.toggle_fog_led(hub.ledRedPin, on=False)

        time.sleep(0.5)


def run_monitor_readings():
    while True:
        hub.monitor_readings()
        time.sleep(5)


def run_cloud_relay():
    while True:
        time.sleep(10)

        dbHelper = DBHelper(db_name='fog.db')
        data_to_relay = dbHelper.select_unrelayed_sensor_data()

        if len(data_to_relay) > 0:
            print("********Relaying sensor data...********")

            data_to_relay = [data.to_dict() for data in data_to_relay]

            requests.post(url=CLOUD_SENSOR_DATE_URI,
                          data=json.dumps(data_to_relay),
                          headers=HEADERS)

            dbHelper.update_relayed_sensor_data(
                [x["id"] for x in data_to_relay])


############################ START OF MQTT ############################


def on_message(client, userdata, msg):

    command = str(msg.payload.decode())
    print('Command subscribed: ' + command)

    if command == 'normal':
        hub.green_led_on = True
        hub.red_led_on = False
    else:
        hub.green_led_on = False
        hub.red_led_on = True


def mqtt_client():
    broker = 'broker.emqx.io'
    port = 1883
    topic = "/is4151-is5451/mockpe/smartlight/lixin"
    client_id = f'python-mqtt-{random.randint(0, 10000)}'
    username = 'emqx'
    password = 'public'
    client = mqtt.Client(client_id)
    client.username_pw_set(username, password)
    client.connect(broker, port)
    client.subscribe(topic)
    client.on_message = on_message
    client.loop_forever()


############################ START OF MAIN ############################

if __name__ == "__main__":
    threading.Thread(target=run_cloud_relay).start()

    threading.Thread(target=run_monitor_readings).start()

    threading.Thread(target=toggle_fog_led).start()

    threading.Thread(target=mqtt_client).start()