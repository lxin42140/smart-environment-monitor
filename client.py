import sys
import random
import time
import json
import requests
import paho.mqtt.client as mqtt

BASE_URI = "http://127.0.0.1:23336"
PREDICT = "/predict"
HEADERS = {'content-type': 'application/json'}

if __name__ == '__main__':

    n = len(sys.argv)

    if n > 1:

        # get arg as list
        args = sys.argv[1:]

        # send post request
        data = {"data": args}
        response = requests.post(url=BASE_URI + PREDICT,
                                 data=json.dumps(data),
                                 headers=HEADERS)

        # get response
        response = response.json()
        response = json.loads(response)
        label = response["cluster"].replace('"', '').strip()
        print("predicted label: {}".format(label))

        # determine command base on label
        command = ""

        if label == "0":
            command = "normal"
        else:
            command = "harsh"

        # init mqtt
        broker = 'broker.emqx.io'
        port = 1883
        topic = "/is4151-is5451/mockpe/smartlight/lixin"
        client_id = f'python-mqtt-{random.randint(0, 10000)}'
        username = 'emqx'
        password = 'public'
        client = mqtt.Client(client_id)
        client.username_pw_set(username, password)
        client.connect(broker, port)

        # publish command
        client.publish(topic, command)
        client.disconnect()

        print('command published: ' + command)