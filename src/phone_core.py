# phone_core.py
#
# Act as a main thread for the telephone app, dispatching IPC, etc.

from dial_monitor import DialMonitor
from hook_monitor import HookMonitor
from queue import Queue
import logging

logging.basicConfig(level=logging.DEBUG)

def main():
    my_input_queue = Queue()
    dial_queue = Queue()
    hook_queue = Queue()

    dial_monitor = DialMonitor(16, dial_queue, my_input_queue)
    hook_monitor = HookMonitor(12, hook_queue, my_input_queue)

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
            else:
                logging.debug("Digit: {}".item)
    except KeyboardInterrupt:
        dial_queue.put("KILL")
        hook_queue.put("KILL")
    dial_monitor.join()
    hook_monitor.join()    

if __name__ == "__main__":
    pass