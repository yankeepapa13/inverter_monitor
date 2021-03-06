#!/usr/bin/python

'''
Copyright (c) 2015, NC Thompson
All rights reserved.
Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:

1) Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

2) Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation 
    and/or other materials provided with the distribution.

3) Neither the name of the ORGANIZATION nor the names of its contributors may 
    be used to endorse or promote products derived from this software without 
    specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import serial
import time
import urllib
import json
import logging

logging.basicConfig(level=logging.INFO)
try:
    ser = serial.Serial("/dev/ttyACM0", 9600)
    logging.info("Connected to serial device")
except serial.SerialException:
    logging.error("Device could not be configured")
    
url = "http://192.168.1.25:9005/"


def stringTime():
    timeNow = time.localtime()
    return time.strftime("%H %M %d %b %Y")

def buildFrame():
    sendString = "="
    sendString = sendString + stringTime()
    multiplusString = getMultiplusInfo()
    sendString = sendString + multiplusString
    sendSum = 0
    for i in range(len(sendString)):
        sendSum = (sendSum - ord(sendString[i])) %256
    sendString = sendString + chr(sendSum)
    return sendString

def formatString(value, length, fLen):
    fString = '{0:0.'+str(fLen) +'f}'
    string = fString.format(value)
    padding = length - len(string)
    if padding != 0:
        for i in range(padding):
            string = ' ' + string
    return string    

def getMultiplusInfo():
    try:
        response = urllib.urlopen(url)
        responseString = response.read()
    except Exception:
        logging.error("URL Error to request JSON")
        return ""
    device = json.loads(responseString)

    leds = device['leds']
    lcdString = str(leds[0])
    lcdString += str(leds[3])
    lcdString += str(leds[7])

    batVoltage = device['batVoltage'] 

    if leds[1] != 0 and leds[7] != 1 or batVoltage <= 12.33:
        lcdString += '3'
    elif leds[5] == 1:
        lcdString += '5'
    elif leds[4] == 1:
        lcdString += '4'
    elif leds[7] == 0:
        if batVoltage > 12.5:
            lcdString += '0'
        elif batVoltage > 12.2:   
            lcdString += '1'
        elif batVoltage > 12.0:   
            lcdString += '2'
    else:
        lcdString += '4'
    

    lcdString += formatString(batVoltage, 5, 2)
    batCurrent = device['batCurrent'] 
    lcdString += formatString(batCurrent, 6, 2)

    inVoltage = device['inVoltage'] 
    lcdString += formatString(inVoltage, 5, 1)
    inCurrent = device['inCurrent'] 
    lcdString += formatString(inCurrent, 4, 2)
    
    outVoltage = device['outVoltage'] 
    lcdString += formatString(outVoltage, 5, 1)
    outCurrent = device['outCurrent'] 
    lcdString += formatString(outCurrent, 4, 2)

    inFreq = device['inFreq'] 
    lcdString += formatString(inFreq, 4, 1)
    outFreq = device['outFreq'] 
    lcdString += formatString(inFreq, 4, 1)
    
    return lcdString
    

while True:
    sendString = buildFrame()    
    for i in range(len(sendString)):
        ser.write(sendString[i])
    time.sleep(10)
