import requests


def send(event_name):
    webhook_url = "https://maker.ifttt.com/trigger/"+event_name+"/with/key/eHJt8MGlmWfbo5dNivgZBC96kp6_Rus_WnrAylMHnwJ"


    response = requests.post(webhook_url.format(event=event_name))

    return response.status_code
