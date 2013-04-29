import RPi.GPIO as GPIO
import time

in1 = 11
in2 = 13
in3 = 15
in4 = 16
in5 = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(in1, GPIO.IN)
GPIO.setup(in2, GPIO.IN)
GPIO.setup(in3, GPIO.IN)
GPIO.setup(in4, GPIO.IN)


prev_input1 = GPIO.input(in1)
prev_input2 = GPIO.input(in2)
prev_input3 = GPIO.input(in3)
prev_input4 = GPIO.input(in4)
while True:
	input1 = GPIO.input(in1)
	input2 = GPIO.input(in2)
	input3 = GPIO.input(in3)
	input4 = GPIO.input(in4)

	if (not prev_input1) and input1:
		print "Boton 1"

	if (not prev_input2) and input2:
		print "Boton 2"

	if (not prev_input3) and input3:
		print "Boton 3"

	if (not prev_input4) and input4:
		print "Boton 4"

	prev_input1 = input1
	prev_input2 = input2
	prev_input3 = input3
	prev_input4 = input4

	time.sleep(0.05)
