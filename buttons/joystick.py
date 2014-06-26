"""
Gamepad Module
Daniel J. Gonzalez
dgonz@mit.edu

Based off code from: http://robots.dacloughb.com/project-1/logitech-game-pad/
"""

import pygame
import time


"""
Returns a vector of the following form:
[LThumbstickX, LThumbstickY, Unknown Coupled Axis???,
RThumbstickX, RThumbstickY,
Button 1/X, Button 2/A, Button 3/B, Button 4/Y,
Left Bumper, Right Bumper, Left Trigger, Right Triller,
Select, Start, Left Thumb Press, Right Thumb Press]

Note:
No D-Pad.
Triggers are switches, not variable.
Your controller may be different
"""

def get(j):
    out = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    it = 0 #iterator
    pygame.event.pump()

    #Read input from the two joysticks
    for i in range(0, j.get_numaxes()):
        out[it] = j.get_axis(i)
        it+=1
    #Read input from buttons
    for i in range(0, j.get_numbuttons()):
        out[it] = j.get_button(i)
        it+=1
    return out

def main():
    pygame.init()
    j0 = pygame.joystick.Joystick(0)
    j1 = pygame.joystick.Joystick(1)
    j0.init()
    j1.init()
    print 'Initialized Joystick : %s' % j0.get_name()
    print 'Initialized Joystick : %s' % j1.get_name()

    timeit = False
    try:
        while True:
            j0output = get(j0)
            j1output = get(j1)
            if any(j0output):
                print 'J0: ', j0output
                timeit = True
            if any(j1output):
                print 'J1: ', j1output
                timeit = True
            if timeit:
                time.sleep(.5)
                timeit = False
    except KeyboardInterrupt:
        j0.quit()
        j1.quit()


if __name__ == '__main__':
    main()
