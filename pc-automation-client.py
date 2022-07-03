from threading import Thread
import websocket
import pyautogui
import rel
import json
from selenium.webdriver import Chrome
import os

driver:Chrome = None
webdriverThread:Thread = None

wd = os.path.dirname(__file__)
config = None
with open(wd+"/config.json","r") as config_file:
    config = json.loads(config_file.read())

def startDriver():
    global driver
    global config
    driver = Chrome(config["chromedriver"])
    driver.get(config["targeturl"])

def mouse_event(event,*args,**kwargs):
    if event == "click":
        pyautogui.click()

def webdriver_event(event,*args,**kwargs):
    if event == "close":
        if driver:
            driver.close()

def on_message(ws, message):
    data = json.loads(message)
    print(data)
    if data["event_type"] == "mouse":
        mouse_event(data["event"],*data["args"],**data["kwargs"])
    elif data["event_type"] == "webdriver":
        webdriver_event(data["event"],*data["args"],**data["kwargs"])


def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###\n",close_status_code,close_msg)

def on_open(ws):
    global webdriverThread
    print("Opened connection")
    webdriverThread = Thread(target=startDriver,daemon=True).start()

def main():
    global config
    code = input("Enter code: ")
    host = config["host"]
    port = config["port"]

    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"ws://{host}:{port}/ws/pcautomation/{code}/",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()

if __name__ == "__main__":
    main()

#{'event_type': 'mouse', 'event': 'click', 'args': [], 'kwargs': {}}