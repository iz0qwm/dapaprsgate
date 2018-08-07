#!/bin/bash
#
##############################################################################
#                                                                            #
#                         Pi-Star DAPNET API Tool                            #
#                                                                            #
#     Version 1.0, Code, Design and Development by Andy Taylor (MW0MWZ).     #
#       Helpfull input from Florian Wolters (DF2FET) - Thank you Flo.        #
#                                                                            #
##############################################################################
#
if [ "$(id -u)" != "0" ]; then
  echo -e "You need to be root to run this command...\n"
  exit 1
fi

# Get the stored DAPNET API Config
DAPNETAPIFile=/opt/dapnet/dapaprsgate/dapnetapi.key
if [ -f ${DAPNETAPIFile} ]; then
        USER=$(grep -m 1 'USER=' ${DAPNETAPIFile} | awk -F "=" '/USER/ {print $2}')
        PASS=$(grep -m 1 'PASS=' ${DAPNETAPIFile} | awk -F "=" '/PASS/ {print $2}')
        TRXAREA=$(grep -m 1 'TRXAREA=' ${DAPNETAPIFile} | awk -F "=" '/TRXAREA/ {print $2}')
else
        echo "Unable to find your DAPNET API Info, no API commands available."
        exit 0
fi

if [ -z "$2" ]
then
        echo ""
        echo "Per usare questo script, richiamalo con qualche argomento;"
        echo "Ad esempio:"
        echo "pistar-dapnetapi IZ0QWM IU7IGU \"Messaggio di test\""
        echo "Il comando precedente invierà un messaggio sul pager di IU7IGU contenente \"IZ0QWM: Messaggio di test\""
        echo ""
        echo "For additional feedback add the \"debug\" option:"
        echo "Per informazioni aggiuntive sull'esito aggiungete l'opzione \"debug\" :"
        echo "pistar-dapnetapi IZ0QWM IU7IGU \"Messaggio di test\" debug"
        echo ""
        exit 0
fi

# Setup some variables
APIURL="http://www.dapnet-italia.it/api"
HOST="${1}"
RECIPIENT="${2}"
TEXT="${3}"
#HOST=$(hostname)

# Debug option
if [ "$4" = "debug" ]
then
        echo " Request to DAPNET API: {"
        echo "  \"text\": \"${HOST^^}: ${TEXT}\","
        echo "  \"callSignNames\": ["
        echo "    \"${RECIPIENT}\""
        echo "  ],"
        echo "  \"transmitterGroupNames\": ["
        echo "    \"${TRXAREA}\""
        echo "  ],"
        echo "  \"emergency\": false"
        echo "}"
        echo ""
        echo ""
fi

# Speak to DAPNET
RESULT=$(curl -s -H "Content-Type: application/json" -X POST -u ${USER}:${PASS} -d \
        "{ \"text\": \"${HOST^^}: ${TEXT}\", \"callSignNames\": [\"${RECIPIENT}\"], \"transmitterGroupNames\": [\"${TRXAREA}\"], \"emergency\": false }" \
        ${APIURL}/calls )

# Debug option
if [ "$4" = "debug" ]
then
        echo "Answer from DAPNET API: ${RESULT}"
        echo ""
        echo ""
fi

# Exit Clean
exit 0

