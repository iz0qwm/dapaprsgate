# Gateway between APRS and DAPNET 
###### dapaprsgate

L'idea è di permettere l'invio di messaggi dall'APRS verso il mondo DAPNET (POCSAG) e viceversa.

Messaggi da APRS -> DAPNET
---------------------------
Inviare un messaggio a POCGAT-1<br/>
Nel testo scrivere  DESTINATARIO@testo del messaggio  
  
Es.<br/>
```
       TO: POCGAT-1  
       Testo: IZ0QWM@Questo è un messaggio per IZ0QWM  
```

Per istruzioni via APRS inviare un messaggio a POCGAT-1 con ?

Es.  
```
       TO: POCGAT-1  
       Testo: ?  
```
Si riceverà una risposta con:  
```
	POCSAT GATEWAY: usa CALL@testo messaggio - www.dapnet-italia.it  
```	
  
Messaggi da DAPNET -> APRS
--------------------------

  
