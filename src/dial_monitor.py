# dial_monitor.py
#
# A class to monitor the dial as it turns and report new digits back to the owner

import RPi.GPIO as GPIO
from queue import Queue
from threading import Thread, Lock, Timer
import logging
import time

class ButtonHandler(Thread):
    def __init__(self, pin, func, edge='both', bouncetime=10):
        super().__init__(daemon=True)
        self.edge = edge
        self.func = func
        self.pin = pin
        self.bouncetime = float(bouncetime)/1000
        self.lastpinval = GPIO.input(self.pin)
        self.lock = Lock()

    def __call__(self, *args):
        if not self.lock.acquire(blocking=False):
            return
        t = Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
        pinval = GPIO.input(self.pin)
        if (
                ((pinval == 0 and self.lastpinval == 1) and
                 (self.edge in ['falling', 'both'])) or
                ((pinval == 1 and self.lastpinval == 0) and
                 (self.edge in ['rising', 'both']))
        ):
            self.func(*args)
        self.lastpinval = pinval
        self.lock.release()


class DialMonitor(Thread):
    """A class to monitor the phone dial and report back new digits as they arrive
    """

    def __init__(self, dial_pin, input_queue, output_queue, hook_position="HOOK_OFF", kill_timeout=5, pulse_timeout=0.15) -> None:
        super().__init__()

        # Set some state
        self.digit = 0
        self.dial_pin = dial_pin
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.hook_position = hook_position
        self.kill_timeout = kill_timeout
        self.pulse_timeout = pulse_timeout

        # Create our timer, but don't start it
        self.pulse_timer = Timer(self.pulse_timeout, self.send_digits)

        # Created our Button Handler
        self.button_handler = ButtonHandler(dial_pin, self.collect_pulses, edge='rising', bouncetime=10)
    
    def send_digits(self):
        logging.debug("Sending {}".format(self.digit) )
        self.output_queue.put( self.digit )
        self.digit = 0

    def collect_pulses(self, pin):
        if( self.hook_position == "HOOK_OFF" ):
            if( self.digit != 0 ):
                self.pulse_timer.cancel()
            self.digit += 1
            self.pulse_timer.start()
        else:
            logging.debug("Ignoring pulses as we're on teh hook")

    
    def run(self):
        self.running = True
        GPIO.add_event_detect( self.dial_pin, GPIO.BOTH, self.hook_change )
        
        # Wait for someone to kill me
        while self.running:
            item = self.input_queue.get()
            if( item == "KILL" ):
                self.running = False
            elif( item == "HOOK_ON" ):
                self.hook_position = "HOOK_ON"
            elif( item == "HOOK_OFF" ):
                self.hook_position = "HOOK_OFF"
            else:
                logging.info("Received an unknown message from input_queue: '{}'".format(item))
            
        logging.info('Exiting...')

if __name__ == "__main__":
    # Setup GPIO
    dial_pin = 16
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(dial_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Run a test to see if we can monitor the hook

    logging.basicConfig(level=logging.DEBUG)

    dial_input_queue = Queue()
    dial_output_queue = Queue()
    dial_monitor = DialMonitor(dial_pin, dial_input_queue, dial_output_queue, "HOOK_ON")
    dial_monitor.start()

    dial_digits = 0
    while( dial_digits < 5 ):
        change = dial_output_queue.get(30)
        dial_digits += 1
        logging.info( "Hook change: {}".format(change))
    while( dial_digits < 5 ):
        change = dial_output_queue.get(30)
        dial_digits += 1
        logging.info( "Hook change: {}".format(change))
    dial_input_queue.put("KILL")
    dial_monitor.join()
    GPIO.cleanup()
