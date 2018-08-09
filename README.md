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

Se su APRS vuoi ricevere messaggi dal DAPNET devi:  
*1.* essere registrato anche su DAPNET (con RIC)  
*2.* Scrivere nel messaggio di stato la parola POCGAT  
Es. Raffaello www.kwos.it su DACIA DUSTER - POCGAT
  
Messaggi da DAPNET -> APRS
--------------------------

Inviare un messaggio ma avere l'accortezza di scrivere al termine
la parola *POCGAT*

Es.  
```
  IZ0QWM: Messaggio da inviare anche in aprs - POCGAT
  IU7IGU
  ALL
```
In questo modo il messaggio sarà destinato a IU7IGU sia su rete DAPNET che su APRS.  
Sempre che IU7IGU abbia soddisfatto i punti *1* e *2*  

 
