import time
import serial
import pandas as pd
from threading import Thread
from flask import Flask, jsonify
import json
import os

app = Flask(__name__)
import logging
# logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.DEBUG)


results = []
ser = None
reading = False
score = 0

def read_data(level="default", experiment_name="trial-1"):
    global ser, results, reading, score
    ser = serial.Serial('COM10', 250000)
    time.sleep(2) # Waiting for seriel to connect
    experiment_name = "trial-4"
    experiment_dir = f"experiments/{experiment_name}"
    if not os.path.exists(experiment_dir):
        os.makedirs(experiment_dir)

    if os.path.exists(f"{experiment_dir}/level-{level}@pulse_data.json"):
        os.remove(f"{experiment_dir}/level-{level}@pulse_data.json")

    # save metadata
    metadata = {
        "start_time": time.strftime('%Y-%m-%d %H:%M:%S'),
        "level": level,
        "experiment_name": experiment_name
    }
    with open(f"{experiment_dir}/level-{level}@metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    all_results = []
    while reading:
        if ser.in_waiting > 0:
            results = []
            line = ser.readline().decode('utf-8').strip()
            sensors = line.split(";") #split by two sensors 
            results.extend([data.split(",") for data in sensors]) #split individual data- IBI, BPM, Signal. 
            results = [item for sublist in results for item in sublist]
            all_results.append(results)
            # logging.info(results)
            try:
                # create dataframe from results
                df = pd.DataFrame(all_results, columns=["Sensor_ID_0", "BPM_0", "IBI_0", "Signal_0", "Sensor_ID_1", "BPM_1", "IBI_1", "Signal_1"])
                df["Game_score"] = 0
            except:
                results = []
                continue



            # write to file
            with open(f"{experiment_dir}/level-{level}@pulse_data.json", "w") as f:
                try:
                    data = json.loads(f.read())
                except:
                    data = []
                new_data = df.to_dict(orient='records')
                data.extend(new_data)
                json.dump(data, f, indent=4)

    # write game score to the same file
    with open(f"{experiment_dir}/level-{level}@pulse_data.json", "r") as f:
        data = json.load(f)
        data[-1]["Game_score"] = score

    # Update end time in metadata
    metadata["end_time"] = time.strftime('%Y-%m-%d %H:%M:%S')
    metadata["game_score"] = score
    with open(f"{experiment_dir}/level-{level}@metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    with open(f"{experiment_dir}/level-{level}@pulse_data.json", "w") as f:
        json.dump(data, f, indent=4)

    logging.info("Game score successfully written to pulse_data.json")
    

@app.route('/start/<level>')
def start_reading(level):
    print("start")
    logging.info("start")
    logging.debug("start")
    global reading, ser
    if reading and ser:
        ser.close()
    reading = True
    Thread(target=read_data, args=(level,)).start()
    return 'Reading started.'

@app.route('/stop/<game_score>')
def stop_reading(game_score=None):
    print("stop")
    logging.info("stop")
    logging.debug("start")
    global reading
    global score
    score = game_score
    reading = False
    if ser:
        ser.close()
    return 'Reading stopped.'


if __name__ == '__main__':
    app.run(port=5050, debug=False)