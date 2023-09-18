# GreenhouseSystem
This is a flask app that is built to run my home greenhouse system that is locally hosted on a raspberry pi zero WH and powered from solar panels.

It runs while there is enough electricity. 

# Info
- The code may be clunky (This was designed/built as I went along)
- I use 30watt solar to power this device. It usually will get enough power to boot and run

# Functions
- Runs off 12v motorbike/car battery
- Uses 12v solenoid valve to water plants
- Supports servo controllable window
- Indoor temp/humidty
- Outdoor temp/humidty
- Raspberry pi box temp/humidty
- Raspberry pi stats
- Logging to csv
- Visual data graphs
- Visual web UI

# Modules
- flask
- waitress
- psutil
- Adafruit-DHT
