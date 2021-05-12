# To execute this program, you need the 'psn' python module. If you are running 
# on Windows, copy the corresponding pre-built module found in the 'libs' folder
# in the script folder.

import psn
import time
import socket
from random import random
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
import numbers

######################
###     CONFIG     ###
######################

OSC_ip = "192.168.0.50"         #IP to receive OSC (IP of the Computer that runs the script)
OSC_Port = 1337                 #Port for incomming OSC Messages


SERVER_NAME = "OSC2PSN Server"
MCAST_GRP = '236.10.10.10'      #multicast adress for PSN, default 236.10.10.10
MCAST_PORT = 56565              #multicast port for PSN, default 56565

tracker_config = [              #configure the trackers, list can be extended, first value is the OSC-address, second value is the name of the Tracker
    ('/tracker1','Tracker 1'), 
    ('/tracker2','Tracker 2')
    ] 

######################
###   CONFIG END   ###
######################

def OSChandler(address, *args): # used to handle incomming OSC messages
    #extract position data and put them into the correct tracker object
    #loop thru all configured trackers
    for i, trackerConf in enumerate(tracker_config):
        #store the current position
        x = trackers[i].get_pos().x
        y = trackers[i].get_pos().y
        z = trackers[i].get_pos().z
        if trackerConf[0] == address: #if the address of the current checked tracker fits the address of the message
            for j, argument in enumerate(args): #check all provided arguments
                if isinstance(argument, (int, float)):
                    #argument is int or float so use it as a new position
                    if j == 0:
                        x = argument
                    elif j == 1:
                        y = argument
                    elif j == 2:
                        z = argument 
            trackers[i].set_pos(psn.Float3(x,y,z))
        elif trackerConf[0]+"/x" == address:
            for j, argument in enumerate(args): #check all provided arguments
                if isinstance(argument, (int, float)):
                    #argument is int or float so use it as a new position
                    if j == 0:
                        x = argument
            trackers[i].set_pos(psn.Float3(x,y,z))
        elif trackerConf[0]+"/y" == address:
            for j, argument in enumerate(args): #check all provided arguments
                if isinstance(argument, (int, float)):
                    #argument is int or float so use it as a new position
                    if j == 0:
                        y = argument
            trackers[i].set_pos(psn.Float3(x,y,z))
        elif trackerConf[0]+"/z" == address:
            for j, argument in enumerate(args): #check all provided arguments
                if isinstance(argument, (int, float)):
                    #argument is int or float so use it as a new position
                    if j == 0:
                        z = argument
            trackers[i].set_pos(psn.Float3(x,y,z))


OSCdispatcher = Dispatcher()
OSCdispatcher.set_default_handler(OSChandler)


MULTICAST_TTL = 2 #used for PSN packets

#prepare socket for PSN Data
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)



# Helper functions
def get_time_ms(): return int( time.time() * 1000 )
start_time = get_time_ms()
def get_elapsed_time_ms(): return get_time_ms() - start_time

# Encoder / Decoder
encoder = psn.Encoder( SERVER_NAME )

trackers = {}
#create tracer objects
for i, tracker in enumerate(tracker_config):
    trackertmp = psn.Tracker(i, tracker[1])
    trackertmp.set_pos(psn.Float3(0, 0, 0))
    trackertmp.set_status(0.1)
    trackertmp.set_timestamp(i)
    trackers[trackertmp.get_id()] = trackertmp


async def loop(): #main loop
    # Create one PSN frames with one trackers
    while True:  
        time_stamp = get_elapsed_time_ms()
        packets = []
        packets.extend( encoder.encode_info( trackers, time_stamp ) )
        packets.extend( encoder.encode_data( trackers, time_stamp ) )

        # Decode
        for packet in packets:
            sock.sendto(packet, (MCAST_GRP, MCAST_PORT))
            #send each packet
            #some socket foo
        #time.sleep(0.1)
        await asyncio.sleep(0.1)

async def init_main(): #init async server and main loop
    server = AsyncIOOSCUDPServer((OSC_ip, OSC_Port), OSCdispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    await loop()  # Enter main loop of program

    transport.close()  # Clean up serve endpoint


asyncio.run(init_main())