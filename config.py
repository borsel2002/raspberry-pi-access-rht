# System-wide imports
import configparser
import logging
import os.path
import re

# Local Packages
from controlled_device import ControlledDevice
from strong_link_sl030_reader import StrongLinkSl030Reader

def parse_config_options(config_filename):
    if not os.path.exists(config_filename):
        assert False, "Configuration file %s does not exist" % config_filename
    config = configparser.ConfigParser()
    config.read(config_filename)
    
    # Read 'plain' config parameters first:
    acl_path = config.get('Paths', 'access control files')


    # Now loop through the readers and devices specified in the config
    # file, and dynamically up the contents of the readers and devices
    # dictionaries, based on the specific type of reader/device
    readers_by_name = {}
    devices_by_name = {}

    # So as to avoid copy-and-paste coding, we use a regex match to split
    # the parsing between the two types of parameters.
    # This also has the advantage of catching typos, where if someone 
    # incorrectly types 'Rreader' in a section name or similar, the error
    # will be raised instead of just ignored
    for o in sorted(config.sections()):
        if o == 'Paths':
            continue
        
        m = re.search(r'^(Reader|Device) (.*)', o)
        if not m:
            assert False, "Unsupported config section '%s'" % o
        elif m.group(1) == 'Reader':
            # Readers are "card readers", and the hardware underlying each
            # reader can be of varying types. Based on the 'reader type'
            # parameter, we instantiate the right kind of object.
            #
            # I've decided to hard-code the list of supported object types
            # for sanity checking here, rather than 'eval'ing the supplied
            # name
            if config.get(o, 'reader type') == 'StrongLinkSl030Reader':
                r = StrongLinkSl030Reader(config.items(o))
            else:
                assert False, \
                        "Unsupported Reader type - '%s'" \
                                % self.reader_type

            # Store the reader object we've created into the 'readers_by_name'
            # dictionary, with the key being the name stored in the config
            # file.
            r.name = m.group(2)
            readers_by_name[ m.group(2) ] = r

        elif m.group(1) == 'Device':
            # Devices are the 'things' we control (doors, machinery, etc).
            
            # Build a new Device from the parameters we've been supplied
            # and store it in the 'devices_by_name' has
            d = ControlledDevice(config.items(o), acl_path)
            d.name = m.group(2)
            devices_by_name[ m.group(2) ] = d
        else:
            assert False, \
                    "Section not understood in config file: '%s'" % m.group(1)

    logging.info("Config read successfully")

    return(acl_path, readers_by_name, devices_by_name)

