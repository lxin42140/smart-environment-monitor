import time
import sqlite3
import serial
import math
import requests
import json
# GPIO imports
import RPi.GPIO as GPIO
import threading
from node.Adafruit_BME280 import *
# DB import
from db.db_helper import DBHelper


class Hub:

    def __init__(self, hub_identifier, connect_radio=False) -> None:
        print("********Initiating hub:{}...********".format(hub_identifier))
        try:
            self.hub_identifier = hub_identifier

            # GPIO
            GPIO.setmode(GPIO.BOARD)

            # LED
            self.ledRedPin = 40
            self.red_led_on = False
            self.ledGreenPin = 38
            self.green_led_on = False

            # connect to bme
            self.bme = BME280(t_mode=BME280_OSAMPLE_8,
                              p_mode=BME280_OSAMPLE_8,
                              h_mode=BME280_OSAMPLE_8)

            # connect to radio
            self.connected_radio = connect_radio

            if connect_radio:
                self.connected_node_devices = []
                self.ser = serial.Serial(port='/dev/ttyACM0',
                                         baudrate=115200,
                                         timeout=1)

                while len(self.connected_node_devices) != 1:
                    print("resetting radio...")
                    self.radio_reset()
                    time.sleep(15)
                    print("handshaking...")
                    self.radio_handshake()
                    time.sleep(15)

            # connect to db
            self.db_helper = DBHelper(db_name='fog.db')
        except Exception as err:
            raise Exception("********INIT FAILED: {}********".format(err))

    ############################ START OF FOG COMMANDS ############################
    def monitor_readings(self):
        print("********Getting readings from micro:bit devices...********")

        combined_sensor_data = {}
        all_sensor_data = []

        if self.connected_radio:
            all_sensor_data.extend(self.__get_data_from_node('sensor=light'))

        deviceName = ""
        for sensor_data in all_sensor_data:
            data = sensor_data.split('=')
            deviceName = data[0]
            deviceValue = data[1]

            if deviceName not in combined_sensor_data.keys():
                combined_sensor_data[deviceName] = []

            combined_sensor_data[deviceName].append(deviceValue)

        # get data from BME280
        atemp = round(self.bme.read_temperature(), 3)
        ahum = round(self.bme.read_humidity(), 3)

        print("BME280: temp={}, humidity={}".format(atemp, ahum))

        # append data to the same devicename since theres only one node
        combined_sensor_data[deviceName].append(atemp)
        combined_sensor_data[deviceName].append(ahum)

        print("Combined_sensor_data sensor reading: {}".format(
            combined_sensor_data))

        self.db_helper.insert_sensor_readings(combined_sensor_data)

    ############################ START OF NODE COMMANDS ############################
    def radio_reset(self):
        self.__send_command('reset')

    def radio_handshake(self):
        print("Connecting fog to micro:bit devices...")
        self.__send_command('handshake')

        strMicrobitDevices = None

        while strMicrobitDevices == None or len(strMicrobitDevices) <= 0:
            strMicrobitDevices = self.__wait_response()
            time.sleep(0.1)

        print(strMicrobitDevices)

        # strMicrobitDevices format is enrol=deviceNameA,deviceNameB...
        strMicrobitDevices = strMicrobitDevices.split('=')

        # get list of devices
        if len(strMicrobitDevices[1]) > 0:
            # get individual device name
            self.connected_node_devices = strMicrobitDevices[1].split(',')

            if len(self.connected_node_devices) > 0:
                for mb in self.connected_node_devices:
                    print('Connected to micro:bit device {}...'.format(mb))

    def __get_data_from_node(self, commandToTx: str) -> list:
        print("Getting {}...".format(commandToTx))

        self.__send_command('cmd:' + commandToTx)

        strSensorValues = None

        while strSensorValues == None or len(strSensorValues) <= 0:
            strSensorValues = self.__wait_response()
            time.sleep(0.1)

        listSensorValues = strSensorValues.split(',')
        print(listSensorValues)

        if len(listSensorValues) != len(self.connected_node_devices):
            print("did not receive feedback from all nodes, retrying...")

            listSensorValues = self.__get_data_from_node(commandToTx)

        return listSensorValues

    def toggle_fog_led(self, ledPin, on):
        GPIO.setup(ledPin, GPIO.OUT)

        # With a pull-up resistor, the input pin will read a high state when the button is not pressed
        # set TRUE -> off LED
        # set FALSE -> on LED
        if on:
            GPIO.output(ledPin, False)
        elif not on:
            GPIO.output(ledPin, True)

    def __send_command(self, command):
        command = command + '\n'
        self.ser.write(str.encode(command))

    def __wait_response(self) -> str:
        response = self.ser.readline()
        response = response.decode('utf-8').strip()
        return response

    def __del__(self):
        GPIO.cleanup()
