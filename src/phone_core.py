# phone_core.py
#
# Act as a main thread for the telephone app, dispatching IPC, etc.

import RPi.GPIO as GPIO
from dial_monitor import DialMonitor
from hook_monitor import HookMonitor
from queue import Queue
import logging
from google_assistant import GoogleAssistant

log_format = "%(module)s:%(threadName)s:%(levelname)s %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format)
assistant = GoogleAssistant()

def get_assistance():
    """Reach out to GoogleAssistant for assistance
    """
    logging.info('Begin Assistance')
    keep_going = True
    while( keep_going == True ):
        keep_going = assistant.assist()
        logging.info("Assistance returned. Returned {}".format(keep_going))
    logging.info( "Assistance complete." )

def main():
    # setup GPIO
    hook_pin = 12
    dial_pin = 16
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(dial_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(hook_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup communication queues
    my_input_queue = Queue()
    dial_queue = Queue()
    hook_queue = Queue()

    dial_monitor = DialMonitor(dial_pin, dial_queue, my_input_queue)
    hook_monitor = HookMonitor(hook_pin, hook_queue, my_input_queue)

    try:
        dial_monitor.start()
        hook_monitor.start()
        while True:
            item = my_input_queue.get()
            if( item == "HOOK_ON" ):
                logging.debug( "Hook Down" )
                dial_monitor.set_hook_state(True)
            elif( item == "HOOK_OFF" ):
                logging.debug( "Hook Up" )
                dial_monitor.set_hook_state(False)
            elif( item == 0 ):
                get_assistance()
            else:
                logging.debug("Digit: {}".format(item))
    except KeyboardInterrupt:
        dial_queue.put("KILL")
        hook_queue.put("KILL")
    dial_monitor.join()
    hook_monitor.join()    

if __name__ == "__main__":
    main()
