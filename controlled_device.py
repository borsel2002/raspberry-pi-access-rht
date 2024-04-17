# System-Wide packages
import fileinput
import logging
import logging
import re

# Associated Packages
from quick2wire import gpio

###############################################################################
# Class - ControlledDevice
###############################################################################


class ControlledDevice:
    name = 'NOT DEFINED'
    
    pin_objects = {}
    enable_set_pins_low = []
    enable_set_pins_high = []
    disable_set_pins_low = []
    disable_set_pins_high = []

    acl_filename = None

    authorised_cards = []

    def  __init__(self, config, acl_path):
        """Device Constructor"""
        self.acl_path = acl_path

        for o, a in config:
            if o == 'enable set pins low':
                self.enable_set_pins_low = self.parse_pin_parameters(a)
            elif o == 'enable set pins high':
                self.enable_set_pins_high = self.parse_pin_parameters(a)
            elif o == 'disable set pins low':
                self.disable_set_pins_low = self.parse_pin_parameters(a)
            elif o == 'disable set pins high':
                self.disable_set_pins_high = self.parse_pin_parameters(a)
            elif o == 'acl filename':
                self.acl_filename = a
            else:
                assert False, "Unsupported parameter '%s' for Device" % o

        if not (                                        \
                   len(self.enable_set_pins_low)   > 0  \
                or len(self.enable_set_pins_high)  > 0  \
                or len(self.disable_set_pins_low)  > 0  \
                or len(self.disable_set_pins_high) > 0  \
            ):
            assert False, "%s - None of the following set: " \
                "enable_set_pins_low, " \
                "enable_set_pins_high, " \
                "disable_set_pins_low, " \
                "disable_set_pins_high " % self.name
            
        if not self.acl_filename:
            assert False, "ACL filename not set"


    def parse_pin_parameters(self, pins_as_text):
        if re.search('[^0-9\ ]+', pins_as_text):
             assert False, "Pins parameters supplied is not all-numeric," \
                + " separated by spaces (is '%s')" % pins_as_text
        pins = []
        for pin_number_as_text in pins_as_text.split():
            pin_number = int(pin_number_as_text)
            pins.append(pin_number)

            # Create a communication object
            if pin_number not in self.pin_objects:
                pin = gpio.pins.pin(pin_number)
                pin.open()
                pin.direction = gpio.Out
                self.pin_objects[pin_number] = pin

        return pins


    def check_for_card_in_db(self, card):
        logging.info("Card presented to device %s" % self.name)
        logging.info("Card id %s" % card)
        self._load_card_db()

        if card in self.authorised_cards:
            logging.info("Card IS authorised");
            return self.enable()
        else:
            logging.info("Card is NOT authorised");
            return self.disable()

    def enable(self):
        self._set_pins(0, self.enable_set_pins_low)
        self._set_pins(1, self.enable_set_pins_high)
        return True

    def disable(self):
        self._set_pins(0, self.disable_set_pins_low)
        self._set_pins(1, self.disable_set_pins_high)
        return False

    # Set associated pins low or high
    def _set_pins(self, state, pin_list):
        for pin_number in pin_list:
            self.pin_objects[pin_number].value = state

    # Read the card database, and build a list of authorised cards
    def _load_card_db(self):
        acl_full_path = self.acl_path + '/' + self.acl_filename
        self.authorised_cards = []
        for line in fileinput.input(acl_full_path):
            self.authorised_cards.append(line.rstrip())

