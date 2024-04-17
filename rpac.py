#!/usr/bin/env python3
# System-Wide imports
import getopt
import logging
import pprint
import select
import socket
import sys
import time

# Associated Packages
import quick2wire.gpio as gpio

# Local packages
import config

# Local packages and globals
logging.basicConfig(filename='rpac.log', \
            level=logging.DEBUG)


# Displays help on how to use this program
def usage(extra_message):
    if extra_message:
        print("\nERROR: %s" % extra_message)
    print("""
Options:
    --config=/path/to/rpac.conf
    
Config option defaults to /usr/local/etc/rpac.conf)
""")
    sys.exit(2)


# Parses command-line options
def parse_command_line_arguments():
    config_filename = '/usr/local/etc/rpac.conf'
    
    # Portions of the code for parsing command-line parameters are from
    # the example at
    # http://docs.python.org/2/library/getopt.html
    # © Copyright 1990-2013, Python Software Foundation. 
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hdn:c:", ["help", "config="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-c", "--config"):
            config_filename = a
        else:
            assert False, "Unhandled option"
    # End of example code

    return(config_filename)


# This code builds a set of 'Pin' objects relating to

def build_hardware_pin_map(readers_by_name):
    pin_objects_to_watch = {}
    for reader in readers_by_name:
        trigger_pin = readers_by_name[reader].trigger_pin
        assert trigger_pin not in pin_objects_to_watch, \
            "Pin %s is set as the 'trigger pin' for more " \
            " than one reader or button" % trigger_pin

        pin_objects_to_watch[trigger_pin] = {}
        pin_objects_to_watch[trigger_pin]['handler_object'] = \
                    readers_by_name[reader]


        pin = gpio.pins.pin(trigger_pin)
        pin.open()

        pin.direction = gpio.In
        pin.interrupt = gpio.Both

        pin_objects_to_watch[trigger_pin]['gpio_pin'] = pin

    return pin_objects_to_watch


def wait_for_pin_state_changes(readers_by_name, devices_by_name):
    fds_to_pins = {}

    # Fetch a list of pins to watch, each of which maps to
    # a card reader
    pin_objects_to_watch = build_hardware_pin_map(readers_by_name)

    epoll_handler = select.epoll()
    for pin_num in pin_objects_to_watch:
        handler_object = pin_objects_to_watch[pin_num]['handler_object']
        gpio_pin = pin_objects_to_watch[pin_num]['gpio_pin']

        epoll_handler.register(gpio_pin, select.EPOLLET)
        fds_to_pins[gpio_pin.fileno()] = pin_num


    while True:
        logging.debug("Waiting for event on reader pins")
        events = epoll_handler.poll()
        for filedescriptor, event in events:
            pin_no = fds_to_pins[filedescriptor]
            logging.debug("Got event on pin number %s" % pin_no)
            pin_value = pin_objects_to_watch[pin_no]['gpio_pin'].value
            pin_objects_to_watch[pin_no]['handler_object'].trigger_pin_state_change(
                        pin_value, devices_by_name)


def main():
    # Get the config file, and from it, get the readers, devices,
    # and button objects
    config_filename = parse_command_line_arguments()
    acl_path, readers_by_name, devices_by_name = \
                config.parse_config_options(config_filename)
    
    for device_name in devices_by_name:
        devices_by_name[device_name].disable()
    
    logging.info("Waiting for card to be presented")
    wait_for_pin_state_changes(readers_by_name, devices_by_name)

if __name__ == "__main__":
    main()

