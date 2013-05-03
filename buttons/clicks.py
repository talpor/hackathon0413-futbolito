from __future__ import absolute_import

import RPi.GPIO as GPIO
import time

from . import actions

# ad-hoc function to reset a pin. DRY
def reset_ioin(ioins, ioin, ioin_queues, erase_queues, blocked_queues, now):
    ioin_queues[ioin] = []
    #erase_queues['queues'][ioin][0] = 0
    flipped_time = erase_queues['queues'][ioin][0]
    erase_queues['queues'][ioin] = (flipped_time,True)
    for ioin in ioins:
        blocked_queue[ioin] = now

# Set up the IO pins that are available and wich are in use
ioins = actions.board_players.keys()
count_ins = len(ioins)

# A pin is always on a certain state (ON or OFF) and the pressing of a button
# flips this state. Wether a pin is always ON or OFF depends on the circuit.
# This variable states if the pins are either ON or OFF when the button is not
# pressed.
base_state = True

# Set the numbering mode to use the pin numbers, and register the pins as INs
GPIO.setmode(GPIO.BOARD)
for ioin in ioins:
    GPIO.setup(ioin, GPIO.IN)

# Time
now = time.time()

# List with the previous states for each pin
prev_inputs = []
for ioin in ioins:
    prev_inputs.append(GPIO.input(ioin))

# Dictionary io->(time_flipped,sent) that will be our erase click queue
erase_queues = {'queues':{},'last_time':now}
for ioin in ioins:
    erase_queues['queues'][ioin] = (0,False)

#Dictionary io->times_when_clicked that will be our single/double click queue
ioin_queues = {}
for ioin in ioins:
    ioin_queues[ioin] = []

#Dictionary io->last_time_blocked that will be our blocked queue
blocked_queue = {}
for ioin in ioins:
    blocked_queue[ioin] = 0

dt = 0.35 #in seconds, time between clicks for a double click
et = 1 #in seconds, time for an erase click (mantained click)
bt = 3 #in seconds, time a button is blocked after registering a click, double-click or erase

#****** Main loop ******#
while True:
    #Take the current time
    now = time.time()

    #List that will hold the registered inputs for this cycle
    inputs = []

    #Read the inputs for this cycle
    for ioin in ioins:
        inputs.append(GPIO.input(ioin))


    #Register buttons pressed
    pressed = []
    for ioin,input,prev_input in zip(ioins,inputs,prev_inputs):
        if (not prev_input) and input:
            pressed.append(True)
        else:
            pressed.append(False)


    #Process each pin
    for ioin,press,input in zip(ioins,pressed,inputs):

        #******* Process blocked buttons *******#
        #If the button has been blocked recently, ignore it
        if now - blocked_queue[ioin] < bt:
            if press:
                print "button %s is blocked" % ioin
            continue


        #******** Process erases *******#
        #If we're flipped, update the time
        if input != base_state:
            last_time = erase_queues['last_time']
            flipped_time = erase_queues['queues'][ioin][0]
            sent = erase_queues['queues'][ioin][1]
            erase_queues['queues'][ioin] = ((flipped_time + (now-last_time)) , sent)

        #If we're not flipped, mantain the flipped time in zero
        else:
            #This if covers the case when the erase was already processed, but the button hasn't been released
            if erase_queues['queues'][ioin][1]:
                erase_queues['queues'][ioin] = (0,False)
                continue

            erase_queues['queues'][ioin] = (0,False)

        #Check for erases.
        #The condition is true if: a) The button has been pressed enough time, b) the erase hasn't been detected
        if (erase_queues['queues'][ioin][0] >= et) and (not erase_queues['queues'][ioin][1]):
            reset_ioin(ioins,ioin,ioin_queues,erase_queues,blocked_queue,now)
            actions.undo(ioin)  # print "erase %s" % ioin
            continue

        if input != base_state:
            continue

        #******* Process single/double clicks ********#
        #Take the ioin queue
        ioin_queue = ioin_queues[ioin]

        #If there wasn't any events, just queue this one
        if (len(ioin_queue) == 0) and press:
            ioin_queue.append(now)
            continue

        #If there was ONE event, we need to handle a possible click or double click
        if (len(ioin_queue) == 1):
            #Check if the time for a double click has expired
            #If so, count a single click and block the button
            if now-ioin_queue[0] >= dt:
                reset_ioin(ioins,ioin,ioin_queues,erase_queues,blocked_queue,now)
                actions.goal(ioin)  # print "click %s" % ioin
                continue

            #The time for a double click has not expired
            #If the button was pressed, count a double click and block the button
            elif press:
                reset_ioin(ioins,ioin,ioin_queues,erase_queues,blocked_queue,now)
                actions.goal(ioin, own=True)  # print "double click %s" % ioin
                continue

            #If we get here, it means that the time for a double click hasn't expired,
            #but no pressing has been detected, keep waiting until something happens...
            continue



    #Update the previous inputs
    for i,input in zip(range(count_ins),inputs):
        prev_inputs[i] = inputs[i]


    #Erases needs to keep track of time since the last cycle
    erase_queues['last_time'] = now


    #Wait a second to prevent bouncing
    time.sleep(0.05)
