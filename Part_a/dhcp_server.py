""" This is a Python script that uses the Scapy library to listen for and handle DHCP
 (Dynamic Host Configuration Protocol) packets. DHCP is a network protocol used
 to dynamically assign IP addresses and other network configuration settings
 to devices on a network.
"""

from scapy.all import *
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
import time


# Define constants
DEVICE = "en0"  # the network interface to listen on
SERVER_IP = "127.0.0.2"  # IP address of DHCP server
SERVER_PORT = 67  # Port to listen on
# a list of IP addresses that will be offered to clients
IP_ADDRESS = {'127.0.0.5': True, '127.0.0.6': True,
              '127.0.0.7': True, '127.0.0.8': True, '127.0.0.9': True}

""" listens for DHCP requests on the specified DEVICE and SERVER_PORT.
  It uses Scapy's sniff() function to capture a single packet and store it in the packet variable. 
  If the packet is a DHCP packet, the handle_dhcp_packet() function is called to handle it.
   If the packet is not a DHCP packet, it prints a message indicating that it is not a DHCP packet."""


def handle_dhcp_packet(packet):
    # Handle DHCP packet based on message type
    client_mac = packet[BOOTP].fields['chaddr']
    client_xid = packet[BOOTP].xid
    client_port = packet[UDP].sport
    option = packet[DHCP].options
    messageType = option[0][1]
    print("*************** messageType: ", messageType) 
    
    if messageType == 1:
        handle_dhcp_discover(client_mac, client_xid, client_port)
    elif messageType == 3:
        handle_dhcp_request(client_mac, client_xid, client_port)


def handle_dhcp_discover(client_mac, client_xid, client_port):
    """ DHCP discover is a message that sent by a client when it is first connected to a
    network and needs to obtain an IP address.
    The DHCP Discover message is a broadcast message that is sent to all devices on the network.
    The message requests that any DHCP servers on the network respond with an offer of an available IP address."""

    found = None
    curr_time = datetime.now()
    for ip, available in IP_ADDRESS.items():
        if available:
            IP_ADDRESS[ip] = False
            found = ip
            break
    if not found:
        print("No IP addresses available")
        return
    
    print(curr_time , ": " , f"Offering IP address: {found}")

    print("creating a dhcp offer packet...")
    # The DHCP offer packet is a unicast packet that is sent to the client that sent the DHCP discover message.

    eth = Ether(src=str(get_if_hwaddr(DEVICE)), dst=client_mac)
    ip = IP(src=SERVER_IP, dst="255.255.255.255")
    udp = UDP(sport=SERVER_PORT, dport=client_port)
    boot = BOOTP(chaddr=client_mac, xid=client_xid, yiaddr=found, siaddr='127.0.0.3', op=2)
    dhcp = DHCP(options=[("message-type", "offer"),
                         ("server_id", SERVER_IP),
                         ("requested_addr", found),
                         'end'])
    packet_offer = eth / ip / udp / boot / dhcp

    curr_time = datetime.now()
    print(curr_time , "sending the dhcp offer packet...")
    sendp(packet_offer, iface=DEVICE)
    


def handle_dhcp_request(client_mac, client_xid, client_port):
    """If the client device receives one or more DHCP Offer packets,
    it will select one and send a DHCP Request packet to the DHCP server.
     This packet indicates which IP address the client has chosen,
      and it asks the server to confirm that it is still available.
      The Request packet is broadcasted to all devices on the network,
     but it is directed at the specific DHCP server that sent the corresponding Offer packet."""

    print("*****************ACK packet build ***************************************")
    client_ip = packet[DHCP].options[2][1]
    if client_ip in IP_ADDRESS:
        # remove the ip address from the list of available ip addresses
        IP_ADDRESS[client_ip] = False
        print(f"IP address: {client_ip}")
    if not client_ip:
        print("No IP addresses available")
        return False

    # Create a DHCP ACK packet
    eth = Ether(src=str(get_if_hwaddr(DEVICE)), dst=client_mac)
    ip = IP(src=SERVER_IP, dst="255.255.255.255")
    udp = UDP(sport=SERVER_PORT, dport=client_port)
    bootp = BOOTP(chaddr=client_mac, xid=client_xid, op = 5)
    dhcp = DHCP(options=[("message-type", 5), 
                         'end'])
    packetAck = eth / ip / udp / bootp / dhcp
    sendp(packetAck, iface=DEVICE)
    print("ACK packet sent")
    print("*****************ACK packet sent ***************************************")
    

if __name__ == "__main__":
   # Listen for DHCP requests on specified device and port
    while True:
        # print the current time
        curr_time = datetime.now()
        print(curr_time , " - Listening for DHCP requests...")
        try:
            # Listen for DHCP requests and store the first packet in the my_packet variable
            packet = sniff(iface=DEVICE, filter=f"udp and port {SERVER_PORT}", count=1)[0]
        except IndexError:  # No packets received
            continue

        # Wait for DHCP request to be fully received
        time.sleep(1)

        # Check if packet is a DHCP packet
        if packet and packet.haslayer(DHCP):
              # Handle DHCP packet based on message type
            handle_dhcp_packet(packet)

        else:
            # print the time of the packet
            print("time: " + packet.time + "- we found a packet, but it is not a DHCP packet")
            print("please press 1 to continue listening for DHCP requests or 2 to exit")
            # get the user's input
            user_input = input()
            # if the user entered 2, exit the program
            if user_input == "2":
                exit()
            # if the user entered 1, continue listening for DHCP requests
            elif user_input == "1":
                continue
            # if the user entered something else, print an error message and exit the program
            else:
                print("Error: invalid input")
                exit()