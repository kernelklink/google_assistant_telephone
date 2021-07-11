
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
    pin_number = 18
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    try:
        while True:
            pin_current = GPIO.input(pin_number)
            if pin_current == 1:
                phone_picked_up()
            else:
                phone_hung_up()
            while GPIO.input(pin_number) == pin_current:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print('Exiting...')
        GPIO.cleanup()


if __name__ == "__main__":
    listen_for_hook_state_change()
