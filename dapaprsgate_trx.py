#!/usr/bin/python
import websocket
import json
import string
import re
import sys
import os
import requests

try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    	json_message = json.loads(message) 
    	log_message = json_message['Log']
	string_message = str(log_message)
	if string_message.find("data") == -1:
		pass
	else:
                prev_mittente = "addr: "
		left,sep,right = string_message.partition(prev_mittente)
		destinatario = right[:6]
		prima,messaggio = string_message.split('data:')
                clean1_messaggio = messaggio.replace("\" }']", "")
                clean2_messaggio = clean1_messaggio.replace(" \"", "")
		if destinatario == "2504, " or destinatario == "165856":
			pass
		else:
			ric = str(destinatario)
			file_config = open('/opt/dapnet/Core/local/data/State.json',"r").readlines()
			for i in range(len(file_config)):
        			if file_config[i].startswith(ric, 20):
                			prima = file_config[i-6]
                			dopo = prima.splitlines()[0]
                			nome,call = dopo.split(":")
                			clean1_call = call.replace(" \"", "")
                			clean2_call = clean1_call.replace("\",","")
					clean2_call_upper = clean2_call.upper()
			print("RIC: %s - Destinatario: %s - Messaggio: %s" % (destinatario, clean2_call_upper, clean2_messaggio))


def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
	    string_to_send = "{\"GetStatus\"}"
            #ws.send("Hello %d" % i)
            ws.send(string_to_send)
        time.sleep(5)
        #ws.close()
        #print("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8055/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
