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
from time import sleep
from datetime import datetime
from aprslib.packets.base import APRSPacket
from aprslib.util import latitude_to_ddm, longitude_to_ddm, comment_altitude
import urllib2
import json
import base64
import math
import threading
import re
import sys
import configparser
import os

# Leggo il file di configurazione
cfg = configparser.RawConfigParser()
try:
        #attempt to read the config file config.cfg
        config_file = os.path.join(os.path.dirname(__file__),'dapaprsgate.cfg')
        cfg.read(config_file)
except:
        #no luck reading the config file, write error and bail out
        logger.error('dapaprsgate could not find / read config file')
        sys.exit(0)

#logging.basicConfig(filename='dapaprsgate.log',level=logging.INFO) # level=10
logger = logging.getLogger('dapnet')
handler = logging.FileHandler('dapaprsgate.log')
logformat = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(logformat)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Leggo le credenziali per DAPNET 
hampagerusername = cfg.get('user','username')
hampagerpassword = cfg.get('user','password')
hampagerurl = cfg.get('dapnet','baseurl') + cfg.get('dapnet','trxurl')

# Leggo le credenzialie per APRS-IS
aprsisusername = cfg.get('aprsis','username')
aprsispassword = cfg.get('aprsis','password')
aprsissourcecallsign = cfg.get('aprsis','sourcecall')
aprsishost = cfg.get('aprsis','host')

class APRSMessage(object):
    def __init__(self):
        self.message = None
 
    def set_message(self, message):
        self.message = message
	aprs_data = aprslib.parse(message)
	if message.find("POCSAG") == -1:
		pass
		#print "--------- %s" % message
	else:
		# Vede il campo From ma seleziona solo gli Italiani
		da = aprs_data.get('from') 
		regex = re.compile('^I')
		if re.match(regex, da):
			logger.info('###################')
			logger.info(' ATTIVO PER POCSAG')
			logger.info('###################')
       			logger.debug('Received message: %s', message)
			logger.info('Attivo: %s', aprs_data.get('from'))
			logger.info('###################')

#
# Invio messaggio su DAPNET se inviato a POCGAT-1
#
	if message.find("POCGAT-1") == -1:
                pass
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
		import subprocess	               	
		invio = ['./send_dapnet_api.sh', aprs_data.get('from'), to, messaggio]
		subprocess.Popen(invio)
		logger.info('-------------------------------------------')

# send_dapnet_api.sh FROM TO test debug
 
    def message_timer(self):
        if self.message is None:
            logger.debug('No message received!')
        else:
            self.message = None

#def callback(packet):
#    print packet

am = APRSMessage()
at = threading.Timer(10.0, am.message_timer)
at.start()

AIS = aprslib.IS(aprsisusername, passwd=aprsispassword, host=aprsishost, port=10152)
try:
        AIS.connect()
except:
        logger.error('Invalid APRS credentials')
        sys.exit(0)
else:
        #connection to APRS-IS has been established, now continue
	logger.info('Connesso al server APRS-IS: %s', aprsishost)


#AIS.consumer(callback, raw=False)
AIS.consumer(callback=am.set_message, raw=True)

#request = urllib2.Request(hampagerurl)
#base64string = base64.b64encode('%s:%s' % (hampagerusername, hampagerpassword))
#request.add_header("Authorization", "Basic %s" % base64string)
#response = urllib2.urlopen(request)
#dapnetdata = json.loads(response.read())
#print (dapnetdata[0])
#AIS.sendall(data)
