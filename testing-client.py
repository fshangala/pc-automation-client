from tkinter import *
import websocket
import threading
from json.encoder import JSONEncoder

root = Tk()
root.title("WebRemote")

status = Label(root)
status.grid(column=0,columnspan=2,row=0)

wsapp = websocket.WebSocket()
wsthread = None

def on_message():
    global wsapp
    while True:
        data = wsapp.recv()
        print(data)

def connectServer(code:str,host="localhost",port=8000):
    global wsapp
    global wsthread

    if code == "":
        code = "sample"
    wsapp.connect(f"ws://{host}:{port}/ws/pcautomation/{code}/")
    if wsapp.connected:
        wsthread = threading.Thread(target=on_message,daemon=True).start()
        #wsapp.send("{\"message\":\"hello\"}")

def sendCommand():
    global wsapp
    command = {
        "event_type":"mouse",
        "event":"click",
        "args":[],
        "kwargs":{}
    }
    data = JSONEncoder().encode(command)
    wsapp.send(data)

codeEntry = Entry(root)
codeEntry.grid(column=0,row=1)
button = Button(root,text="Connect",command=lambda:connectServer(codeEntry.get()))
button.grid(column=1,row=1)

mycommand = Button(root,text="Send Command",command=sendCommand)
mycommand.grid(column=0,columnspan=2,row=2)

root.mainloop()