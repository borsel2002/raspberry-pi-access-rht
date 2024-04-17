# Notes on Security:

This system was specifically built to be used in a minimal-security
environment (a shared communal space). It was also specifically designed so as
to allow the use of existing IZTECH 'Student Cards' so as to avoid
the purchase of new RFID cards by the user.

Furthermore, it was also designed to operate without interfering with the normal
operation of those cards. If this were not the case the contents of the cards
could be overwritten by the user to ensure secure operation.

Given these (unusual) requirements, this code operates simply based on the
unique 'ID' supplied by the card. It does NOT use the MiFare encryption
facilities provided by the card. Since a determined attacker with electronics
knowledge could be able to fake a card ID, I do not recommend you use this
where security is important.



# Installation

This code requires a Raspberry Pi to operate. It may work on other similar
hardware supported by the GPIO libraries with minor modification.

1) Install required programs as per 'SETUP.md'

2) Edit rapc.conf and configure the pin assignments for the
    card reader and relay.

2) Start the rpac.py script by running start.sh, which configures the
    requisite environment variables for you:

    # NOTE THAT THIS DOES NOT NORMALLY DISPLAY ANY OUTPUT
    ./start.sh    
    
    In a separate session, run 'less rpac.log' to see what the
    system is doing

