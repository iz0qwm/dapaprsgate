#!/usr/bin/python
import aprslib
import websocket
import json
import string
import re
import sys
import os
import requests
import logging
import configparser
from random import randint
import subprocess
version = subprocess.check_output(["git", "describe"]).strip()

# Leggo il file di configurazione
cfg = configparser.RawConfigParser()
try:
        #attempt to read the config file config.cfg
        config_file = os.path.join(os.path.dirname(__file__),'dapaprsgate.cfg')
        cfg.read(config_file)
except:
        #no luck reading the config file, write error and bail out
        print(os.path.basename(__file__) + " could not find / read config file")
        sys.exit(0)

# Leggo la posizione del log file
logfile = cfg.get('misc', 'logfile')

#logging.basicConfig(filename='dapaprsgate.log',level=logging.INFO) # level=10
logger = logging.getLogger('aprslib.inet.IS')
handler = logging.FileHandler(logfile)
logformat = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(logformat)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Leggo le informazioni per DAPNET
statefile = cfg.get('dapnet','statefile')
transmitterws = cfg.get('dapnet','transmitterws')
# Leggo le credenzialie per APRS-IS
aprsisusername = cfg.get('aprsis','username')
aprsispassword = cfg.get('aprsis','password')
aprsishost = cfg.get('aprsis','host1')
aprsisport = cfg.get('aprsis','port1')
aprspresencefile = cfg.get('aprsis','presencefile')

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
        #print destinatario
        prima,messaggio = string_message.split('data:')
        clean1_messaggio = messaggio.replace("\" }']", "")
        clean2_messaggio = clean1_messaggio.replace(" \"", "")
        if destinatario == "2504, " or destinatario == "165856" or destinatario == "8, fun":
            pass
        else:
            ric = str(destinatario)
            file_config = open(statefile,"r").readlines()
            for i in range(len(file_config)):
                    if file_config[i].startswith(ric, 20):
                        prima = file_config[i-6]
                        dopo = prima.splitlines()[0]
                        nome,call = dopo.split(":")
                        clean1_call = call.replace(" \"", "")
                        clean2_call = clean1_call.replace("\",","")
                        clean2_call_upper = clean2_call.upper()
            #print("RIC: %s - Destinatario: %s - Messaggio: %s" % (destinatario, clean2_call_upper, clean2_messaggio))
            # if clean2_messaggio.find("POCGAT") == -1:
                #logger.info('-------------------------------------------')
                #logger.info("RIC: %s - Destinatario: %s - Messaggio: %s", destinatario, clean2_call_upper, clean2_messaggio)
                #logger.info("Messaggio solo per rete POCSAG")
                #logger.info('-------------------------------------------')
            #else:
            logger.info('dapaprsgate_trx %s engaged...', version)
            logger.info('-------------------------------------------')
            logger.info(' MESSAGGIO DAPNET ----> APRS ')
            logger.info('-------------------------------------------')
            #
            logger.info("RIC: %s - Destinatario: %s - Messaggio: %s", destinatario, clean2_call_upper, clean2_messaggio)
            for line in file(aprspresencefile, "r"):
                    line_strip = line.rstrip()
                    if clean2_call_upper in line_strip:
                        logger.info("Destinatario %s trovato nella lista: %s", clean2_call_upper, line_strip)
                        AIS = aprslib.IS(aprsisusername, passwd=aprsispassword, host=aprsishost, port=int(aprsisport))
                        try:
                            AIS.connect()
                        except:
                            logger.error('Invalid APRS credentials')
                            sys.exit(0)
                        else:
                        #connection to APRS-IS has been established, now continue
                            logger.info('Connesso al server APRS-IS: %s', aprsishost)

                        # ATTENZIONE il nominativo tra due :: deve essere sempre 8 caratteri + uno spazio
                        lunghezza = len(line_strip)
                        if lunghezza == 5:
                            spazio = "    "
                        elif lunghezza == 6:
                            spazio = "   "
                        elif lunghezza == 7:
                            spazio = "  "
                        elif lunghezza == 8:
                            spazio = " "
                        else:
                            spazio = ""
                        # ATTENZIONE creazione numero random da mettere dopo le parentesi graffe
                        rand = str(randint(0, 9))
                        # Creazione del messaggio di risposta ed invio
                        AIS.sendall('POCGAT-1>APOCSG::' + line_strip + spazio + ': ' + clean2_messaggio + ' {' + rand + '')
                        # logger.info('POCGAT-1>APOCSG:: %s %s :%s {%s', line_strip, spazio, clean2_messaggio, rand)
                        logger.info('-------------------------------------------')
                        logger.info('MESSAGGIO INVIATO SU APRS')
                        logger.info('-------------------------------------------')
                    else:
                        logger.info("Destinatario %s NON trovato", clean2_call_upper)
                        logger.info('-------------------------------------------')


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
    ws = websocket.WebSocketApp(transmitterws,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
