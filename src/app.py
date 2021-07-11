
import RPi.GPIO as GPIO
import time
import logging
from google_assistant import GoogleAssistant


assistant = GoogleAssistant()
logging.basicConfig(level=logging.INFO)

hook_status = None

def phone_picked_up():
    """Called when the phone is picked up"""
    logging.info('Receiver picked up')
    keep_going = True
    while( keep_going == True ):
        keep_going = assistant.assist()
        logging.info("Assistance returned. Returned {}".format(keep_going))
    logging.info( "Assistance complete." )            

def phone_hung_up():
    """Called when the phone is hung up"""
    logging.info('Receiver hung up')


def listen_for_hook_state_change():
    """Continuously listens for pickup/hangup of the hook"""
    hook_pin = 12
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(hook_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect( hook_pin, GPIO.BOTH )
    try:
        while True:
            if( GPIO.event_detected( hook_pin ) ):
                pin_current = GPIO.input(hook_pin)
                if pin_current == 1:
                    phone_picked_up()
                else:
                    phone_hung_up()
    except KeyboardInterrupt:
        print('Exiting...')
        GPIO.cleanup()


if __name__ == "__main__":
    listen_for_hook_state_change()
