from scapy.all import *
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from random import randint
import time

DEVICE = "en0"
CLIENT_PORT = 68
DHCP_PORT = 67


def get_client_mac():
    # Get MAC address of client
    # Returns MAC address as a string
    # Returns None if MAC address could not be retrieved
    try:
        return str(get_if_hwaddr(DEVICE))
    except:
        print(f"Error: Failed to get MAC address for device {DEVICE}")
        return None


def send_dhcp_discover():
    try:
        print("Broadcasting DHCP discover...")
        eth = Ether(src=get_client_mac(), dst="ff:ff:ff:ff:ff:ff")
        ip = IP(src="0.0.0.0", dst="255.255.255.255")
        udp = UDP(sport=CLIENT_PORT, dport=DHCP_PORT)
        bootp = BOOTP(chaddr=get_client_mac(), xid=randint(0, 2 ** 32))
        dhcp = DHCP(options=[("message-type", "discover"), "end"])
        packet_discover = eth / ip / udp / bootp / dhcp
        sendp(packet_discover, iface=DEVICE)
        return True
    except:
        print("Error: Failed to send DHCP discover packet")
        return False


def get_dhcp_offer():
    try:
        print("Waiting for DHCP offer...")
        packet_offer = sniff(iface=DEVICE,
                             filter=f"udp and port {CLIENT_PORT} ",
                             timeout=10, count=1)[0]
        print("DHCP offer received")
        return packet_offer
    except:
        print("Error: Failed to get DHCP offer")
        return None


def send_dhcp_request(packet_offer):
    try:
        print("Sending DHCP request...")
        eth = Ether(src=get_client_mac(), dst="ff:ff:ff:ff:ff:ff")
        ip = IP(src="0.0.0.0", dst="255.255.255.255")
        udp = UDP(sport=CLIENT_PORT, dport=DHCP_PORT)
        boot = BOOTP(chaddr=get_client_mac(), xid=packet_offer[BOOTP].xid)
        dhcp = DHCP(options=[("message-type", "request"), ("server_id", packet_offer[BOOTP].siaddr),
                             ("requested_addr", packet_offer[BOOTP].yiaddr), "end"])
        packet_request = eth / ip / udp / boot / dhcp
        sendp(packet_request, iface=DEVICE)
        return True
    except:
        print("Error: Failed to send DHCP request packet")
        return False


def get_dhcp_ack():
    try:
        print("Waiting for DHCP ACK...")
        ack = sniff(iface=DEVICE, filter=f"udp and port {CLIENT_PORT}"
                    , timeout=10, count=1)[0]
        print("DHCP ACK received")
        return ack
    except:
        print("Error: Failed to get DHCP ACK")
        return None
    

def get_ip_from_dhcp():
    if get_client_mac() is None:
        return None

    if not send_dhcp_discover():
        return None

    packet_offer = get_dhcp_offer()
    if packet_offer is None:
        return None

    if not send_dhcp_request(packet_offer):
        return None

    ack = get_dhcp_ack()
    if ack is None:
        return None
    print(f"IP address: {ack[BOOTP].yiaddr} (lease time: {ack[DHCP].options[2][1]} seconds)")

if __name__ == "__main__":
    get_ip_from_dhcp()