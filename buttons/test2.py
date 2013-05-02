import RPi.GPIO as GPIO
import time

#Set up the IO pins that are available and wich are in use
in1 = 11
in2 = 13
in3 = 15
in4 = 16
in5 = 18
ioins = [in1,in2,in3,in4]
count_ins = len(ioins)

#Set the numbering mode to use the pin numbers, and register the pins as INs
GPIO.setmode(GPIO.BOARD)
for ioin in ioins:
	GPIO.setup(ioin, GPIO.IN)

#List with the previous states for each pin
prev_inputs = []
for ioin in ioins:
	prev_inputs.append(GPIO.input(ioin))

#****** Main loop ******#
while True:
	#List that will hold the registered inputs for this cycle
	inputs = []

	#Read the inputs for this cycle
	for ioin in ioins:
		inputs.append(GPIO.input(ioin))
	
	#Check for changes in the inputs
	for ioin,input,prev_input in zip(ioins,inputs,prev_inputs):
		if (not prev_input) and input:
			print "Boton %s" % ioin

	#Update the previous inputs
	for i,input in zip(range(count_ins),inputs):
		prev_inputs[i] = inputs[i]

	#Wait a second to prevent bouncing
	time.sleep(0.05)
