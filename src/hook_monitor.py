# hook_monitor
# 
# Monitors the hook

import RPi.GPIO as GPIO
from queue import Queue
from threading import Thread
import logging
import time

class HookMonitor(Thread):
    """Monitor the hook switch and signal when the phone is off/on the hook
    """

    def __init__(self, hook_pin, input_queue, output_queue, timeout=5) -> None:
        """Constructor for HookMonitor object, assumes that the caller has already setup the GPIO pin, but we still need to setup the interrupts.

        Args:
            hook_pin (int): the GPIO pin number to monitor for the hook switch
            input_queue (queue): input queue to receive communication from the owner
            output_queue (queue): output queue to signal hook changes to the owner
        """
        super().__init__()

        # Save some state
        self.hook_pin = hook_pin
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.timeout = timeout
        self.name="HookMonitor"
    
    def hook_change(self):
        if( self.running ):
            pin_current = GPIO.input(self.hook_pin)
            self.output_queue.put( "OFF" if pin_current == 1 else "ON" )

    
    def run(self):
        """Setup the interrupt for the hook GPIO pin and monitor it, communicating state back to the caller
        """
        self.running = True
        GPIO.add_event_detect( self.hook_pin, GPIO.BOTH, self.hook_change )
        
        # Wait for someone to kill me
        while self.runing:
            item = self.input_queue.get()
            if( item == "KILL" ):
                self.running = False
            else:
                logging.info("Received an unknown message from input_queue: '{}'".format(item))
            
            # sleep for a while
            time.sleep(self.timeout)
            
        logging.info('Exiting...')
        GPIO.cleanup()

if __name__ == "__main__":
    # Run a test to see if we can monitor the hook

    hook_input_queue = Queue()
    hook_output_queue = Queue()
    hook_pin = 12
    hook_monitor = HookMonitor(hook_pin, hook_input_queue, hook_output_queue)

    hook_changes = 0
    while( hook_changes < 5 ):
        change = hook_output_queue.get()
        hook_changes += 1
        logging.info( "Hook change: {}".format(change))
    hook_input_queue.put("KILL")
