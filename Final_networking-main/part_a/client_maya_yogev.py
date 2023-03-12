from scapy.all import *
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.layers.dns import DNS, DNSQR
from random import randint
import time

DEVICE = "en0"
CLIENT_PORT = 68
DHCP_PORT = 67
DNS_PORT = 53
CLIENT_IP = None
DNS_IP = "127.0.0.3"


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
        return packet_offer , packet_offer[BOOTP].yiaddr
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
        packetRequest = eth / ip / udp / boot / dhcp
        time.sleep(1)
        sendp(packetRequest, iface=DEVICE)
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
    

def get_app_ip():
    print("Broadcasting DNS request...")

    # Create a DNS request packet
    eth = Ether(src=get_client_mac(), dst="ff:ff:ff:ff:ff:ff")
    ip = IP(src=CLIENT_IP, dst=DNS_IP)
    udp = UDP(sport=CLIENT_PORT, dport=DNS_PORT)
    dom = input("Enter a domain: ")
    dns = DNS(rd=1, qd = DNSQR(qname=dom))
    packet_dns = eth / ip / udp / dns

    time.sleep(1)
    # Send the packet and wait for a response
    sendp(packet_dns, iface=DEVICE)

    # Wait for a DNS response packet
    print("Waiting for DNS response...")
    packet_response = sniff(iface=DEVICE, filter=f"udp and port {CLIENT_PORT}", count=1)[0] # get the dns response
    print("DNS response received")

    if packet_response and packet_response.haslayer(DNS):
        # Get the IP address from the DNS response packet
        application_IP = packet_response[DNS].an.rdata

        return application_IP



# def get_ip_from_dhcp():
#     if get_client_mac() is None:
#         return None

#     if not send_dhcp_discover():
#         return None

#     packet_offer , CLIENT_IP = get_dhcp_offer()
#     if packet_offer is None:
#         return None

#     if not send_dhcp_request(packet_offer):
#         return None

#     ack = get_dhcp_ack()
#     if not ack:
#         return None
    
    # get_app_ip()

if __name__ == "__main__":
    if get_client_mac() is None:
        exit(1)
    
    if not send_dhcp_discover():
        exit(1)
    
    packet_offer , CLIENT_IP = get_dhcp_offer()
    
    if not send_dhcp_request(packet_offer):
        exit(1)
        
    ack = get_dhcp_ack()
    if not ack:
        print("Error: Failed to get DHCP ACK")
        
    print("The http app IP is: ", get_app_ip())