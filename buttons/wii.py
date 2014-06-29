import cwiid
import gevent
import time

button_delay = .3

def init():
    print 'Waiting for 2 Wiimotes'
    print 'Press 1 & 2 buttons at the same time on each...'
    print '...'
    wm1 = wm2 = None
    while not (wm1 and wm2):
        if not wm1:
            wm1 = cwiid.Wiimote()
            wm1.led = 1
        if not wm2:
            wm2 = cwiid.Wiimote()
            wm2.led = 2
    wm1.rpt_mode = cwiid.RPT_BTN
    wm2.rpt_mode = cwiid.RPT_BTN
    print 'ready!'

    # spawn responders
    gevent.joinall([
        gevent.spawn(respond_to_actions, wm1, 'barca'),
        gevent.spawn(respond_to_actions, wm2, 'madrid')
    ])

def respond_to_actions(wiimote, team):
    print 'hearing from', team, wiimote
    while True:
        buttons = wiimote.state['buttons']
        if buttons & cwiid.BTN_A:
            print 'striker goal on %s!' % team
            time.sleep(button_delay)
        if buttons & cwiid.BTN_B:
            print 'defense goal on %s!' % team
            time.sleep(button_delay)
        if buttons & cwiid.BTN_1:
            print 'striker own goal for %s =(' % team
            time.sleep(button_delay)
        if buttons & cwiid.BTN_2:
            print 'defense own goal for %s =(' % team
            time.sleep(button_delay)
        if buttons & cwiid.BTN_MINUS:
            print 'undo'
            time.sleep(button_delay)
        # If Plus and Minus buttons pressed
        # together then rumble and quit.
        if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):
            print '\nClosing connection %s...' % team
            wiimote.rumble = 1
            time.sleep(1)
            wiimote.rumble = 0
            exit(wiimote)
        gevent.sleep(0)

if __name__ == '__main__':
    init()
