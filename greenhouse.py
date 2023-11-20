import time, datetime, os, psutil, Adafruit_DHT, csv, json, webhook
import RPi.GPIO as io

class gh:
    # File/File paths
    logFilePath = "/home/green/static/data/logs/"
    crashFilePath = "/home/green/static/data/crashLogs/"
    logFilesRow = ["indoorHumid","indoorTemp","outsideHumid","outsideTemp","boxHumid","boxTemp","cpuTemp","cpuFreq","storageUsed","time"]
    configPath = "/home/green/static/data/config.json"
    # - - - - - - - 

    # Config data
    configFile = open(configPath)
    configData = json.load(configFile)
    # - - - - - - - 

    # Variables setup
    allData = []
    deviceData = []
    data = []
    autoWatering = False
    watering = False
    window = False # False is closed | True is open
    update = False # Used for webhook
    time_end = time.time()
    crash = [False, None, None]
    alerted = False
    crashAlerted = False
    lastCrashTime = 0
    # - - - - - - - 

    # Last check values
    lastOutsideHumidity = 0
    lastOutsideTemperature = 0
    lastInsideHumidity = 0
    lastInsideTemperature = 0
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
    gh.servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.05)  # Wait for 50ms before changing angle again


def water(state): # Used to turn on/off the water system
    if state:
        #Turn water on
        gh.watering = True
        io.output(gh.waterRelay, io.HIGH)
    else:
        #Turn water off
        gh.watering = False
        io.output(gh.waterRelay, io.LOW)

def getDeviceData(): # Used to get device data
    freq = psutil.cpu_freq()
    disk = psutil.disk_usage('/')

    cpuTemp = round(psutil.sensors_temperatures()['cpu_thermal'][0].current, 2)

    cpuFreq = round(freq.current, 2)

    usedDisk = round(disk.used / (1024*1024*1024), 2) #GB    
    
    return [cpuTemp,cpuFreq,usedDisk]

def getData(configData): # Used to get tempuratues from sensors
    tempHigh = configData['tempSettings']['high']
    tempLow = configData['tempSettings']['low']

    windowTemp = configData['heatControl']['high']
    insideHumidity, insideTemperature = Adafruit_DHT.read_retry(gh.sensor, gh.insideSensor)
    outsideHumidity, outsideTemperature = Adafruit_DHT.read_retry(gh.sensor, gh.outsideSensor)
    boxHumidty, boxTemperature = Adafruit_DHT.read_retry(gh.sensor, gh.boxSensor)

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
            outsideHumidity = gh.lastOutsideHumidity
            outsideTemperature = gh.lastOutsideTemperature
        except:
            None
    else:
        gh.lastOutsideHumidity = outsideHumidity
        gh.lastOutsideTemperature = outsideTemperature
    
    if int(insideHumidity) > 100:
        try:
            insideHumidity = gh.lastInsideHumidity
            insideTemperature = gh.lastInsideTemperature
        except:
            None
    else:
        gh.lastInsideHumidity = insideHumidity
        gh.lastInsideTemperature = insideTemperature
    
    server = configData['webhook']['server']

    if gh.update:
        if outsideTemperature <= tempLow:
            key = configData['webhook']['keys']['under']
            response = webhook.send(server, key)
            if response == 200:
                gh.update = False

    else:
        if outsideTemperature >=tempHigh:
            key = configData['webhook']['keys']['over']
            response = webhook.send(server, key)
            if response == 200:
                gh.update = True
    
    if insideTemperature >= windowTemp and gh.window == False: #Open window
        for angle in range(90, -1, -1):
            duty_cycle = angle / 18.0 + 2.5
            gh.servo_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(2)
        gh.window = True
        
    if insideTemperature <= (windowTemp - 1) and gh.window == True: #Close window
        time.sleep(0.2)
        for angle in range(0, 90):
            duty_cycle = angle / 18.0 + 2.5
            gh.servo_pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.05)  # Wait for 50ms before changing angle again
        gh.servo_pwm.ChangeDutyCycle(0)
        time.sleep(5)
        gh.window = False
    

    return [round(insideHumidity,1), round(insideTemperature,1), round(outsideHumidity,1), round(outsideTemperature,1), round(boxHumidty,1), round(boxTemperature,1)]

def log(data : list, current_time : float): # Used to save/log data
    dataToSave = []

    for x in data:
        for i in x:
            dataToSave.append(i)

    formatted_date = current_time.strftime("%Y-%m-%d")
    formatted_time = current_time.strftime("%H:%M:%S")
    dataToSave.append(formatted_time)

    filename = gh.logFilePath+formatted_date+".csv"


    if not os.path.exists(filename):
        row = gh.logFilesRow
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

    # data.append(formatted_time)
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(dataToSave)

def checkSchedule(configData, current_time : float): # Used to update watering schedule

    day_of_week = current_time.strftime("%A")
    time = current_time.strftime("%H:%M")

    schedule = configData['schedule']
    duration = configData['watering']['duration']
    if schedule[day_of_week] != "false":
        if str(time) == schedule[day_of_week] and gh.autoWatering == False:
            gh.time_end = time.time() + duration
            gh.autoWatering = True
            water(True)
        elif gh.autoWatering:
            if time.time() >= gh.time_end:
                water(False)
                gh.autoWatering = False

def systemState(): # return layout - [Status, Running, Crashed, Error]

    if gh.crash[0] != True:
        try:
            return ([200, True, False])
        except Exception as e:
            return([500, None, True, str(e)])
    else:
        return ([200, False, gh.crash[0], gh.crash[1]])

def currentData():
    dataToShare = [gh.watering, gh.autoWatering]

    for x in gh.allData:
        for i in x:
            dataToShare.append(i)
    dataToShare.append(0) # Used to be fan speed | Remove soon
    dataToShare.append(gh.window)
    dataToShare.append(datetime.datetime.now().strftime("%H:%M"))
    return dataToShare

def getSchedule():
    with open(gh.configPath) as config_file:
        configData = json.load(config_file)

    return [configData['schedule'], configData['watering']]


def updateJson(data):

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    try:
        # Load the existing JSON data from the file
        with open(gh.configPath, "r") as infile:
            config = json.load(infile)
        i = 0
        while i < 7:
            config['schedule'][days[i]] = data[0][i]
            i+=1
        
        config['watering']['duration'] = int(data[1])

        # Write the modified object back to the JSON file
        with open(gh.configPath, "w") as outfile:
            json.dump(config, outfile, indent=4)
    except Exception as e:
        return [500, str(e)]
    
    return [200, "None"]

def logCrash(configData, crashData : list): #Changed this to save actual time not time in long format

    # [True, "getData() | local variable 'innerL' referenced before assignment", 1689893586.5361037] | 2023-07-20

    crash_time = crashData[2]
    if crash_time != gh.lastCrashTime:
        gh.lastCrashTime = crash_time

        time = datetime.datetime.now()

        formatted_date = time.strftime("%Y-%m-%d")

        time_obj = datetime.datetime.fromtimestamp(crash_time)
        crash_time = time_obj.strftime("%H:%M:%S")

        filename = f"{gh.crashFilePath}{formatted_date}.txt"
        row = f"{str(crashData[1])}, {str(crash_time)}\n"

        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as file:
                file.write(row)
        else:
            with open(filename, 'a', newline='') as file:
                file.write(row)
        
    if gh.crashAlerted == False:
        server = configData['webhook']['server']
        key = configData['webhook']['keys']['crash']
        response = webhook.send(server, key)
        if response == 200:
            gh.crashAlerted = True



def start(): 
    runTime = time.time()

    while True:

        if time.time() >= runTime:

            try:
                with open(gh.configPath) as config_file:
                    configData = json.load(config_file)

                runTime = time.time() + configData['updateFreq']['time']
            except Exception as e:
                gh.crash = [True, "config | " +str(e), time.time()]
            
            if gh.crash[0]:
                logCrash(configData, gh.crash)

            try: 
                if time.time() >= gh.crash[2] + 30: gh.crash = [False, None, None]
            except: None

            current_time = datetime.datetime.now()

            # Collect data
            try:
                gh.deviceData = getDeviceData()
            except Exception as e:
                gh.crash = [True, "getDeviceData() | " +str(e), time.time()]
            
            try:
                gh.data = getData(configData)
            except Exception as e:
                gh.crash = [True, "getData() | " + str(e), time.time()]
            
            gh.allData = [gh.data,gh.deviceData]
            
            try:
                checkSchedule(configData, current_time)
            except Exception as e:
                gh.crash = [True, "checkSchedule() | " +str(e), time.time()]

            try:
                log(gh.allData, current_time)
            except Exception as e:
                gh.crash = [True, "log() | " +str(e), time.time()]

        time.sleep(0.2)