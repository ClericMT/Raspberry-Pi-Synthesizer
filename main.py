#!/usr/bin/env python3
import time
import liblo as OSC
import sys
import RPi.GPIO as GPIO           # import RPi.GPIO module
  
GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # set a port/pin as an input 

from smbus import SMBus
bus = SMBus(1)
# this device should be address 0x48

def readChannel(params):
 global bus
 bus.write_byte(0x48, params & 0x03) # select the channel
 bus.write_byte(0x48, 0) # give it time to convert
 return bus.read_byte(0x48)

def analogOut(out):
 global bus
 bus.write_byte(0x48, 0x40)
 bus.write_byte(0x48, out & 0xFF)
 bus.write_byte(0x48, 0x00)

def readAll(): 
 global bus
 bus.write_byte(0x48, 0x04) # auto-increment command
 data = []
 for _ in range(4):
  data.append(bus.read_byte(0x48))
 return data
 
try:
 target = OSC.Address(1234)
except OSC.AddressError as err:
 print(err)    
 sys.exit()

# start the transport via OSC
OSC.send(target, "/rnbo/jack/transport/rolling", 1)

# classes
class Button:
	def __init__(self, GPIO, name):
		self.GPIO = GPIO # pin id
		self.name = name
		
	def value(self):
		return GPIO.input(self.GPIO)
		
class Pot:
	def __init__(self, channel, name):
		self.channel = channel
		self.name = name
	
	# send value to RNBO patch via OSC	
	def updateParam(self):
		newValue = OSC.send(target, "/rnbo/inst/0/params/{}".format(self.name), self.getValue())
		return newValue
	
	# read pot value	
	def getValue(self):
		return readAll()[self.channel]

# params
inputSig = Pot(1, "inputSig")
controlSig = Pot(2, "controlSig")
frequency = Pot(3, "frequency")
speed = Pot(0, "speed")

while(True):
 inputSig.updateParam()
 controlSig.updateParam()
 frequency.updateParam()
 speed.updateParam()



