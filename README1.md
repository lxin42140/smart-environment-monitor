# smart-environment-monitor

This is a simple prototype that uses IoT Sensors and Machine Learning to determine whether the environment is harsh or normal, and toggle actuators accordingly.

It compromises of 3 components:
1. Edge nodes using microbit and grove sensors (light intensity sensor)
2. Edge server using raspberry pi attached with actuators and sensors (LEDs and BME280 for temperature and humidity reading)
3. Cloud server running on local machine

## Component Functionality

Node devices:
1. retrieve reading from sensor and relay to edge server through radio communication

Edge Server
1. Periodically poll data from node devices using radio to serial communication
2. Persist data to local database
3. Periodically relay data to cloud server using HTTP REST apis
4. subscribe to commands from cloud server using MQTT

Clouder Server
1. Collect and display sensor data collected from various edge servers
2. Periodically trains clustering model based on collected sensor data and save the model as joblib
3. Provides REST endpoints using flask for edge server to relay data and for client to make prediction
4. Provide client for user to make prediction using trained model and publish corresponding commands to the edge server using MQTT

The clustering model is trained based on 3 collected sensor data: light intensity, temperature and humidity and provides 2 clusters.
1 cluster is deemed as harsh, while the other cluster is deemed as normal.
When the user submits new values for prediction, the model generates a label. 
If the label is harsh, then the cloud server will relay a command to the edge server o switch on a red lED and off the green LED
If the label is normal, then the cloud server will relay a command to the edge server o switch on a green lED and off the red LED


## Module Description

### db
The solution is sqlite. A DB helper is provided as a data access layer

### node
Contains javascript program to run on a microbit device to sense light intensity and display light intensity as bar graph
Contains javascript program to run on a microbit device that is meant to connect with raspberry bi as radio anthena. Responsible for converting serial communication to radio requests, and relay radio responses to raspberry pi through serial

### client.py
Contains python program that makes a request to the cloud server for prediction, and publish corresponding commands via MQTT

### cloud_processor.py
Contains a fask application for REST apis, and program for training clustering model

### fog_processor.py
Contains python program that periodically poll data from sensors, relay data to cloud server, and toggle actuators based on subscribed MQTT topics

### hub.py
Contains python program to process serial-to-radio/radio-to-serial communication (radio handshake, relay command, collect data), collecting data from BME280, toggling actuators attached via GPIO, persisting data to database.
