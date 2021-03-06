#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Author: Raffaello Di Martino IZ0QWM starting from the work of DH3WR and PE2KMV
# Date: 06.08.2018
# Version 0.1

import aprslib
import logging
import time
import sched
from time import sleep
from datetime import datetime
from aprslib.packets.base import APRSPacket
from aprslib.util import latitude_to_ddm, longitude_to_ddm, comment_altitude
import urllib2
import urllib3
import json
import base64
import math
import threading
from threading import Timer
import thread
import re
import sys
import configparser
import os
import requests
import websocket
import string
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

#logger = logging.getLogger('dapnet')
logger = logging.getLogger('aprslib.inet.IS')
handler = logging.FileHandler(logfile)
logformat = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(logformat)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Leggo le credenziali per DAPNET 
hampagerusername = cfg.get('user','username')
hampagerpassword = cfg.get('user','password')
hampagerurl = cfg.get('dapnet','baseurl') + cfg.get('dapnet','coreurl')

# Leggo le credenzialie per APRS-IS
aprsisusername = cfg.get('aprsis','username')
aprsispassword = cfg.get('aprsis','password')
aprsissourcecallsign = cfg.get('aprsis','sourcecall')
aprsishost = cfg.get('aprsis','host')
aprsisport = cfg.get('aprsis','port')
aprsisfilter = cfg.get('aprsis','filter')
aprspresencefile = cfg.get('aprsis','presencefile')

# Svuoto il file delle presenze
open(aprspresencefile, 'w').close()

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class APRSMessage(object):

    def cancello_sometimes():
        logger.info("Cancello il file presenze")
        open(aprspresencefile, 'w').close()
	time.sleep(1)

    # Cancello il file delle presenze su APRS ogni 60 minuti
    rt = RepeatedTimer(3600, cancello_sometimes)

    def __init__(self):
        self.message = None
 
    def set_message(self, message):
        self.message = message
	aprs_data = aprslib.parse(message)
	if message.find("POCGAT") == -1:
		pass
		#print "--------- %s" % message
	else:
		# Vede il campo From ma seleziona solo gli Italiani
		da = aprs_data.get('from') 
		# Solo se sei italiano (Il call inizia con "I")
                # sostituito con il filtro su server APRS
		#regex = re.compile('^I')
		#if re.match(regex, da):
	        logger.info('###################')
		logger.info(' ATTIVO PER POCSAG')
		logger.info('###################')
       		logger.debug('Received message: %s', message)
		logger.info('Attivo: %s', aprs_data.get('from'))
		logger.info('###################')

		# Inserisci nominativo nella lista dei reperibili
		call_attivo = aprs_data.get('from')
		if os.path.exists(aprspresencefile):
    			append_write = 'a+' # append if already exists
		else:
    			append_write = 'w+' # make a new file if not
		fileaprs = open(aprspresencefile,append_write)

		lettura = fileaprs.read()
		search_call = call_attivo
		if (search_call in lettura):
			pass
		else:
			fileaprs.write(call_attivo + '\n')
		fileaprs.close()

#
# Invio messaggio su DAPNET se inviato a POCGAT-1
#
	if message.find("POCGAT-1") == -1:
                pass
        else: 
		if message.find("@") == -1:
			if message.find("?") == -1:
				pass
			else:
				logger.info('-------------------------------------------')
				logger.info(' MESSAGGIO APRS ISTRUZIONI ')
				logger.info('-------------------------------------------')
                		logger.info('From: %s', aprs_data.get('from'))
				da = aprs_data.get('from') 
                        	#notifico via APRS a chi lo ha mandato
                        	# ATTENZIONE il nominativo tra due :: deve essere sempre 8 caratteri + uno spazio
                        	lunghezza = len(da)
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
                        	AIS.sendall('POCGAT-1>APOCSG::' + da + spazio + ':POCSAT GATEWAY: usa CALL@testo messaggio - www.dapnet-italia.it {' + rand + '')
				logger.info('-------------------------------------------')

		else:
			logger.info('-------------------------------------------')
			logger.info(' MESSAGGIO APRS ----> DAPNET ')
			logger.info('-------------------------------------------')
       			logger.debug('Received message: %s', message)
                	logger.info('From: %s', aprs_data.get('from'))
	        	logger.debug('Testo completo: %s', aprs_data.get('message_text'))
			messaggio_completo = aprs_data.get('message_text')
			to,messaggio = messaggio_completo.split('@')
			logger.info('To: %s', to)
			logger.info('Messaggio: %s', messaggio)

			# Invio messaggio -> DAPNET
        		#create the complete URL to send to DAPNET
        		http = urllib3.PoolManager()
        		headers = urllib3.util.make_headers(basic_auth= hampagerusername + ':' + hampagerpassword)
			da = aprs_data.get('from') 
			payload = '{ "text": "'+ da +': ' + messaggio +'", "callSignNames": [ "' + to + '" ], "transmitterGroupNames": [ "italia" ], "emergency": false}' 
			#print(headers)
			#print(payload)

			try:
        			#try to establish connection to DAPNET
        			response = requests.post(hampagerurl, headers=headers, data=payload)
			except:
        			#connection to DAPNET failed, write warning to console, write warning to error log then bail out
        			logger.error('Invalid DAPNET credentials or payload not well done')
        			sys.exit(0)
			else:
        			#connection to DAPNET has been established, continue
				logger.info('-------------------------------------------')
				logger.info('MESSAGGIO INVIATO SU DAPNET')
				logger.info('-------------------------------------------')
                #notifico via APRS a chi lo ha mandato
				# ATTENZIONE il nominativo tra due :: deve essere sempre 8 caratteri + uno spazio
				lunghezza = len(da)
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
		        	AIS.sendall('POCGAT-1>APOCSG::' + da + spazio + ':messaggio inviato a ' + to + ' {' + rand + '')	



    def message_timer(self):
        if self.message is None:
            logger.debug('No message received!')
        else:
            self.message = None

am = APRSMessage()
#at = threading.Timer(10.0, am.message_timer)
#at.start()

# Mi collego a APRS-IS
AIS = aprslib.IS(aprsisusername, passwd=aprsispassword, host=aprsishost, port=int(aprsisport))
try:
        AIS.connect()
except:
        logger.error('Invalid APRS credentials or connection not available')
        sys.exit(0)
else:
        #connection to APRS-IS has been established, now continue
        logger.info('dapaprsgate %s starting...', version)
        logger.info('Connesso al server APRS-IS: %s', aprsishost)
"""
When a position sentence is received, it will be passed to the callback function

blocking: if true (default), runs forever, otherwise will return after one sentence
          You can still exit the loop, by raising StopIteration in the callback function

immortal: When true, consumer will try to reconnect and stop propagation of Parse exceptions
          if false (default), consumer will return

raw: when true, raw packet is passed to callback, otherwise the result from aprs.parse()
"""
AIS.set_filter(aprsisfilter)
AIS.consumer(callback=am.set_message, immortal=True, raw=True)



