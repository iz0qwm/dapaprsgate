#!/bin/sh
#
processo=$(ps -ef|grep dapaprsgate.py|head -1|awk '{ print $2 }')
/bin/kill -9 $processo
