import threading
import time
import random
import requests
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from joblib import dump, load
import json
from flask import Flask, render_template, make_response, abort, request, jsonify
from db.db_helper import DBHelper
from sklearn import metrics

############################ START OF CLUSTERING ############################


def train_model():
    print('Starting training process')

    np.random.seed(int(round(time.time())))

    while True:
        try:
            # create df
            df = pd.DataFrame(columns=[
                'id', 'devicename', 'abright', 'atemp', 'ahum', 'timestamp'
            ])

            all_data = DBHelper(
                db_name='global.db').select_all_sensor_readings()

            for data in all_data:
                df = df._append(
                    {
                        'id': data.id,
                        'devicename': data.devicename,
                        'abright': data.abright,
                        'atemp': data.atemp,
                        'ahum': data.ahum,
                        'timestamp': data.timestamp
                    },
                    ignore_index=True)

            # get the independent variables, note that x must be an matrix-like structure, if not we need to reshape
            # e.g. X = df['light'].values.reshape(-1, 1)
            independent_variables = df.drop(['id', 'devicename', 'timestamp'],
                                            axis=1)
            X = independent_variables.values

            # train model
            kmeans = KMeans(n_clusters=2, random_state=0)
            kmeans = kmeans.fit(X)
            print('Silhouette Score = {}'.format(
                metrics.silhouette_score(X, kmeans.labels_)))

            # create a new result df
            result = pd.concat([
                independent_variables,
                pd.DataFrame({'cluster': kmeans.labels_})
            ],
            axis=1)

            # print results
            for cluster in result.cluster.unique():
                print('{:d}\t abright mean: {:.3f} (abright std: {:.3f})'.format(
                    cluster, result[result.cluster == cluster].abright.mean(),
                    result[result.cluster == cluster].abright.std()))

                print('{:d}\t atemp mean: {:.3f} (atemp std: {:.3f})'.format(
                    cluster, result[result.cluster == cluster].atemp.mean(),
                    result[result.cluster == cluster].atemp.std()))
                
                print('{:d}\t ahum mean: {:.3f} (ahum std: {:.3f})'.format(
                    cluster, result[result.cluster == cluster].ahum.mean(),
                    result[result.cluster == cluster].ahum.std()))
                
            # save the trained model
            dump(kmeans, 'model.joblib')

            time.sleep(5)
        except Exception:
            time.sleep(5)
            pass


############################ START OF FLASK ############################

host_name = "0.0.0.0"
port = 23336
app = Flask(__name__)


@app.route("/sensor-data", methods=['GET'])
def get_sensor_data():
    return render_template(
        'sensor_data.html',
        title='Cloud Server',
        all_data=DBHelper(db_name='global.db').select_all_sensor_readings())


@app.route("/sensor-data", methods=['POST'])
def add_sensor_data():
    payload = json.dumps(request.get_json())
    print("Payload: {}".format(payload))

    payload_dict = json.loads(payload)
    print("Parsed payload: {}".format(payload_dict))

    DBHelper(db_name='global.db').insert_cloud_sensor_readings(payload_dict)

    return make_response("sensor data added: {}".format(payload_dict), 200)


@app.route("/predict", methods=['POST'])
def predict():
    # get payload
    payload = json.dumps(request.get_json())

    payload_dict = json.loads(payload)

    # values is an array of the features
    values = payload_dict["data"]

    # predict new temperature and humidity observation
    kmeans = load('model.joblib')

    # temperature, humidity
    newX = [values]
    result = kmeans.predict(newX)

    print('values={}; label={}'.format(values, result[0]))

    data = {"cluster": str(result[0])}
    data = json.dumps(data)

    return jsonify(data)


############################ START OF MAIN ############################

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(
        host=host_name, port=port, debug=False, use_reloader=False)).start()

    threading.Thread(target=train_model).start()