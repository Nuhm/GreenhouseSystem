#Import necessary libraries
from flask import Flask, render_template, jsonify, request
from waitress import serve
from datetime import datetime
import time, os, threading, greenhouse, csv

"""
Librarys to install:
pip install flask
pip install waitress
pip install psutil
pip install Adafruit-DHT
"""


#Initialize the Flask app
app = Flask(__name__)

debugMode = False


print("\n\n")

time.sleep(0.2)

print("\n\n- - -Server started - - -\n")

def dprint(message):
    if debugMode:
        print(message)

def run_in_thread():
    try:
        greenhouse.start()
    except: None

thread = threading.Thread(target=run_in_thread)

# Start greenhouse system on boot
thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/time', methods=['GET'])
def time():
    try:
        schedule = greenhouse.getSchedule()
    except Exception as e:
        return(jsonify(status=500, data=str(e)))
    return(jsonify(status=200, data=schedule))

@app.route('/process-data', methods=['PUT'])
def process_data():
    data = request.get_json()

    response = greenhouse.updateJson(data)

    if response[0] == 200:
        return (jsonify(status=200, data="None"))
    else:
        return (jsonify(status=500, data=response[1]))

@app.route('/systemState', methods=['GET'])
def systemState():
    try:
        function = greenhouse.systemState() # return layout - [Status, Running, Crashed, Error]
    except Exception as e: return(jsonify(status=400, data = False, error=str(e)))

    if function[0] != 200: return(jsonify(status=function[0], data = False, error=function[3]))

    else: 
        if function[2]: # If state is crashed then...
            return(jsonify(status=200, data = False, error=function[3]))
        
        return(jsonify(status=200, data=function[1], error=False))


@app.route('/currentData', methods=['GET'])
def currentData():
    try:
        function = greenhouse.currentData() # return layout - data = [watering, autowatering, indoorTemp, indoorHumid, outsideTemp, outsideHumid, fanspeed, window]
    except Exception as e: return(jsonify(status=500,data=str(e)))

    return(jsonify(status=200, data=function))

@app.route('/water/<value>', methods=['GET'])
def water(value):
    try:
        if value == "true":
            value = True
        else:
            value = False
        greenhouse.water(value)
    except Exception as e:
        return jsonify(status=500, data=str(e))
    return jsonify(status=200, data=None)

@app.route('/data-between/<startDate>/<endDate>', methods=['GET'])
def dataBetween(startDate, endDate): # "2023-04-09", "2023-04-16"
    logsPath = "static/data/logs/"
    data_send = []

    if startDate != endDate:
        files = os.listdir(logsPath)
        file_paths = [os.path.join(logsPath, f) for f in files]

        dates = []
        try:
            for file in file_paths:
                newDate  = file.replace(logsPath, "").replace(".csv", "")
                dates.append(newDate)  
            dates.sort()
            start_date = datetime.strptime(startDate, "%Y-%m-%d").date()
            end_date = datetime.strptime(endDate, "%Y-%m-%d").date()

            for date in dates:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()

                if start_date <= target_date <= end_date:
                    try:
                        with open(logsPath+date+".csv", newline='', errors='ignore') as csvfile:
                            # Read the file contents and remove the NUL character
                            contents = csvfile.read().replace('\x00', '')

                            # Convert the contents into a stream and pass it to the CSV reader
                            data_reader = csv.reader(contents.splitlines(), delimiter=',', quotechar='"')
                            data = list(data_reader)
                            data.pop(0)  # remove the first element
                        data_send.append([data, date])
                    except:
                        None
        except Exception as e:
            return jsonify(status=500,data=str(e))
        data_send = sorted(data_send, key=lambda x: x[1])

    else:
        try:
            with open(logsPath+startDate+'.csv', newline='', errors='ignore') as csvfile:
                # Read the file contents and remove the NUL character
                contents = csvfile.read().replace('\x00', '')

                # Convert the contents into a stream and pass it to the CSV reader
                data_reader = csv.reader(contents.splitlines(), delimiter=',', quotechar='"')
                data = list(data_reader)
                data.pop(0)  # remove the first element
                
            data_send = [[data, startDate]]
        except Exception as e:
            return jsonify(status=500,data=str(e))
    
    return jsonify(status=200,data=data_send)


@app.route('/allData', methods=['GET'])
def allData():
    None


if debugMode:
    app.run(host='0.0.0.0', port=8080, debug=True)
else:
    if __name__ == "__main__":
        serve(app, host="0.0.0.0", port=8080)