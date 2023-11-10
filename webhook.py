import requests
import time


def send(server,event_key):
    rCode = -1

    start = time.time()
    rCode = -1
    while rCode !=200 and time.time() < start + 1:
        webhook_url = f"{server}/api/webhook/{event_key}"
        response = requests.post(webhook_url)
        rCode = response.status_code
        time.sleep(0.5)
    
    return rCode