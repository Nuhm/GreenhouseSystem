import time, datetime, os, psutil, Adafruit_DHT, csv, json, webhook
import RPi.GPIO as io
global crash

# File/File paths
logFilePath = "/home/green/static/data/logs/"
logFilesRow = ["indoorHumid","indoorTemp","outsideHumid","outsideTemp","boxHumid","boxTemp","cpuTemp","cpuFreq","storageUsed","time"]
configPath = "/home/green/static/data/config.json"
# - - - - - - - 

# Config data
configFile = open(configPath)
configData = json.load(configFile)
# - - - - - - - 

# Variables setup
fanSpeed = 100
deviceData = []
data = []
autoWatering = False
watering = False
window = False # False is closed | True is open
update = False # Used for webhook
time_end = None
crash = [False, None]
running = True
# - - - - - - - 

# Pin setup
boxSensor = 2
insideSensor = 3
outsideSensor = 4
waterRelay = 27
servo_pin = 18
# - - - - - - - 

# Sensors setup
io.setmode(io.BCM)
io.setup(waterRelay, io.OUT)
io.setup(servo_pin, io.OUT)
sensor = Adafruit_DHT.DHT22
# - - - - - - - 

# Create a PWM instance
servo_pwm = io.PWM(servo_pin, 50)  # 50 Hz PWM frequency
servo_pwm.start(0) # Starting PWM signal with duty cycle of 0 (corresponds to 0 degrees)
# - - - - - - - 

for angle in range(0, 90): #Close window on boot
    duty_cycle = angle / 18.0 + 2.5
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.05)  # Wait for 50ms before changing angle again


def water(state): # Used to turn on/off the water system
    global watering
    print(state)
    if state:
        #Turn water on
        watering = True
        io.output(waterRelay, io.HIGH)
    else:
        #Turn water off
        watering = False
        io.output(waterRelay, io.LOW)

def getDeviceData(): # Used to get device data
    global deviceData
    global pwm
    global fanSpeed

    fanSpeed = 0

    freq = psutil.cpu_freq()
    disk = psutil.disk_usage('/')

    cpuTemp = round(psutil.sensors_temperatures()['cpu_thermal'][0].current, 2)

    cpuFreq = round(freq.current, 2)

    usedDisk = round(disk.used / (1024*1024*1024), 2) #GB    
    
    deviceData = [cpuTemp,cpuFreq,usedDisk]

def getData(): # Used to get tempuratues from sensors
    global data
    global lastOutsideHumidity
    global lastOutsideTemperature
    global lastInsideHumidity
    global insideTemperature
    global update
    global window

    tempHigh = configData['tempSettings']['high']
    tempLow = configData['tempSettings']['low']
    num_retries = configData['readRetries']['retries']

    windowTemp = configData['heatControl']['high']
    insideHumidity, insideTemperature = Adafruit_DHT.read_retry(sensor, insideSensor)
    outsideHumidity, outsideTemperature = Adafruit_DHT.read_retry(sensor, outsideSensor)
    boxHumidty, boxTemperature = Adafruit_DHT.read_retry(sensor, boxSensor)

    if insideHumidity is None and insideTemperature is None:
        insideHumidity = 0
        insideTemperature = 0
    if outsideHumidity is None and outsideTemperature is None:
        outsideHumidity = 0
        outsideTemperature = 0
    if boxHumidty is None and boxTemperature is None:
        boxHumidty = 0
        boxTemperature = 0

    if int(outsideHumidity) > 100:
        try:
            outsideHumidity = lastOutsideHumidity
            outsideTemperature = lastOutsideTemperature
        except:
            None
    else:
        lastOutsideHumidity = outsideHumidity
        lastOutsideTemperature = outsideTemperature
    
    if int(insideHumidity) > 100:
        try:
            insideHumidity = lastInsideHumidity
            insideTemperature = lastInsideTemperature
        except:
            None
    else:
        lastInsideHumidity = insideHumidity
        lastInsideTemperature = insideTemperature
    

    if update:
        if outsideTemperature <= tempLow:
            response = webhook.send("greenhouseUnder")
            if response == 200:
                update = False

    else:
        if outsideTemperature >=tempHigh:
            response = webhook.send("greenhouseOver")
            if response == 200:
                update = True
    
    if insideTemperature >= windowTemp and window == False: #Open window
        for angle in range(90, -1, -1):
            duty_cycle = angle / 18.0 + 2.5
            servo_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(2)
        window = True
        
    if insideTemperature <= (windowTemp - 1) and window == True: #Close window
        time.sleep(0.2)
        for angle in range(0, 90):
            duty_cycle = angle / 18.0 + 2.5
            servo_pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.05)  # Wait for 50ms before changing angle again
        servo_pwm.ChangeDutyCycle(0)
        time.sleep(5)
        window = False
    

    data = [round(insideHumidity,1), round(insideTemperature,1), round(outsideHumidity,1), round(outsideTemperature,1), round(boxHumidty,1), round(boxTemperature,1)]

def log(data): # Used to save/log data
    global crash

    dataToSave = []

    for x in data:
        for i in x:
            dataToSave.append(i)

    formatted_date = current_time.strftime("%Y-%m-%d")
    formatted_time = current_time.strftime("%H:%M:%S")
    dataToSave.append(formatted_time)

    filename = logFilePath+formatted_date+".csv"

    try:
        if not os.path.exists(filename):
            row = logFilesRow
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)

        # data.append(formatted_time)
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(dataToSave)
    except Exception as e:
        crash = [True, "logging | " +str(e), time.time()]

def checkSchedule(): # Used to update watering schedule
    global autoWatering
    global time_end

    day_of_week = current_time.strftime("%A")
    time = current_time.strftime("%H:%M")

    schedule = configData['schedule']
    durationStr = configData['watering']['duration']

    if schedule[day_of_week] != "false":
        if str(time) == schedule[day_of_week] and autoWatering == False:
            # Parse the duration string into a datetime.timedelta object
            time_obj = datetime.datetime.strptime(time, '%H:%M').time()
            duration = datetime.datetime.strptime(durationStr, '%H:%M')
            duration_delta = datetime.timedelta(hours=duration.hour, minutes=duration.minute)

            # Calculate the end time by adding the duration delta to the start time
            time_end = (datetime.datetime.combine(datetime.date.today(), time_obj) + duration_delta).time()
            time_end = time_end.strftime("%H:%M")
            autoWatering = True
            water(True)
        elif autoWatering:
            if str(time) == str(time_end):
                water(False)
                autoWatering = False

def systemState(): # return layout - [Status, Running, Crashed, Error]
    global crash

    if crash[0] != True:
        try:
            global running
            return ([200, running, False])
        except Exception as e:
            return([500, None, True, str(e)])
    else:
        return ([200, False, crash[0], crash[1]])

def currentData():
    global allData
    global watering
    global autoWatering
    global fanSpeed
    global window

    dataToShare = [watering, autoWatering]

    for x in allData:
        for i in x:
            dataToShare.append(i)
    dataToShare.append(fanSpeed)
    dataToShare.append(window)
    dataToShare.append(datetime.datetime.now().strftime("%H:%M"))
    return dataToShare

def getSchedule():
    data = [configData['schedule'], configData['watering']]
    return data


def updateJson(data):
    global configPath

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    try:
        # Load the existing JSON data from the file
        with open(configPath, "r") as infile:
            config = json.load(infile)
        i = 0
        while i < 7:
            config['schedule'][days[i]] = data[0][i]
            i+=1
        
        config['watering']['duration'] = data[1]

        # Write the modified object back to the JSON file
        with open(configPath, "w") as outfile:
            json.dump(config, outfile, indent=4)
    except Exception as e:
        return [500, str(e)]
    
    return [200, "None"]



def start(): 
    global configFile
    global configData
    global current_time
    global crash
    global allData
    runTime = time.time()

    while running:

        if time.time() >= runTime:
            runTime = time.time() + configData['updateFreq']['time']

            try: 
                if time.time() >= crash[2] + 30 :crash = [False, None, None]
            except: None
            try:
                configFile = open(configPath)
                configData = json.load(configFile)
            except Exception as e:
                crash = [True, "config | " +str(e), time.time()]

            # Trigger the water system
            current_time = datetime.datetime.now()
            try:
                getDeviceData()
            except Exception as e:
                crash = [True, "getDeviceData() | " +str(e), time.time()]
            
            try:
                getData()
            except Exception as e:
                crash = [True, "getData() | " + str(e), time.time()]
            
            try:
                checkSchedule()
            except Exception as e:
                crash = [True, "checkSchedule() | " +str(e)]

            allData = [data,deviceData]

            log(allData)

        time.sleep(0.2)