import RPi.GPIO as GPIO
import MFRC522
import logging

class RC522CardReader:
    def __init__(self, config):
        self.name = config['name']
        self.trigger_pin = config['trigger pin']
        self.spi_port = config['spi port']
        self.spi_device = config['spi device']
        self.spi_speed = config['spi speed']
        self.spi_mode = config['spi mode']
        self.associated_device = config['associated device']

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.trigger_pin, GPIO.BOTH, callback=self.trigger_pin_state_change)

    @staticmethod
    def create_reader(config):
        reader = RC522CardReader(config)
        devices_by_name[reader.associated_device].register_reader(reader)
        return reader

    def check_for_card_in_db(self, card):
        logging.debug("Checking for card %s in database" % card.uid)

        # Check if the card exists in the database
        # If it does, enable the associated device
        # If it doesn't, disable the associated device

        # For demonstration purposes, we'll assume the card is valid
        devices_by_name[self.associated_device].enable()

    def disable(self):
        logging.debug("Disabling device")

    def register_reader(self, reader):
        self.readers.append(reader)

    def trigger_pin_state_change(self, channel):
        logging.debug("State change - %s" % GPIO.input(self.trigger_pin))

        device = devices_by_name[self.associated_device]

        # If the pin state drops to false, then it means a card has been
        # presented - try and read the card
        card = None
        if not GPIO.input(self.trigger_pin):

            logging.debug("Reading card on reader %s" % self.name)
            card = self.read_card()

            if card:
                device.check_for_card_in_db(card)

        else:
            logging.debug("Disabling device %s" % self.associated_device)
            # The card has been removed - we need to ensure that the
            # associated device is turned off
            devices_by_name[self.associated_device].disable()
            logging.debug("Device %s disabled" % self.associated_device)

    def read_card(self):
        logging.info("Fetching card id from %0X" % self.spi_device)

        with MFRC522.MFRC522() as mfrc522:
            try:
                mfrc522.init()

                (status, uid) = mfrc522.request(mfrc522.REQIDL)

                if status == mfrc522.MI_OK:
                    card_as_hex = ['{:02x}'.format(x) for x in uid]

                    logging.debug("Card presented: %s" % ' '.join(card_as_hex))

                    return MFRC522Card(card_as_hex, self.name)

            except Exception as e:
                logging.warning('Error while reading RC522 card: %s' % str(e))

        return None


class MFRC522Card:
    def __init__(self, card_as_hex, reader_name):
        self.reader_name = reader_name
        self.uid = card_as_hex

    def __str__(self):
        return ' '.join(self.uid).upper()


# Main Door Configuration
main_door_config = {
    'name': 'Main Door',
    'trigger pin': 0,
    'spi port': 0,
    'spi device': 0,
    'spi speed': 1000000,
    'spi mode': 0,
    'associated device': 'Main Door'
}

# DJ Room Configuration
dj_room_config = {
    'name': 'DJ Room',
    'trigger pin': 0,
    'spi port': 0,
    'spi device': 1,
    'spi speed': 1000000,
    'spi mode': 0,
    'associated device': 'DJ Room Door'
}

# Broadcast Room Configuration
broadcast_room_config = {
    'name': 'Broadcast Room',
    'trigger pin': 0,
    'spi port': 0,
    'spi device': 0,
    'spi speed': 1000000,
    'spi mode': 0,
    'associated device': 'Broadcast Room Door'
}

# Initialize the readers
main_door_reader = RC522CardReader.create_reader(main_door_config)
dj_room_reader = RC522CardReader.create_reader(dj_room_config)
broadcast_room_reader = RC522CardReader.create_reader(broadcast_room_config)

# For demonstration purposes, we'll assume the card is valid
devices_by_name = {
    'Main Door': main_door_reader,
    'DJ Room Door': dj_room_reader,
    'Broadcast Room Door': broadcast_room_reader
}

for device in devices_by_name.values():
    device.disable()