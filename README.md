# pyAS3992
Provides easy access to AS3992 RFID reader via USB adapter from Python running on Unix machines.
This is a part of a larger project. 
I published this API since there is no convinient API currently published for communicating with this card, especially not for Python.

## Parts I Used
This API was used in order to communicate with the AS3992 UHF RFID reader via UART.

My setup included the following items:
* AS3992 Long Range UHF RFID reader UART (ISO18000-6C EPC G2), purchased [here](http://www.soliddepot.com/index.php?main_page=product_info&products_id=27)
* SolidDigi Xbee USB Adapter FT232RL chip, purchased [here](http://www.soliddepot.com/index.php?main_page=product_info&cPath=46_48&products_id=44)
* Raspberry Pi, running this Python code on Raspbian
(This code was only tested on Raspbian and Ubuntu, it probably won't work on a non-Linux OS, since it currently relys on /dev/ttyUSB. It might be useful to change this in the future, but I have no meaning to maintain this)

## Connections
```
################            ####################           ##########
# Raspberry Pi #  --USB-->  # Xbee USB Adapter # --UART--> # AS3992 #
################            ####################           ##########
```

## Result
Using this API, I was able to sample the AS3992 RFID reader for passive tags nearby.
