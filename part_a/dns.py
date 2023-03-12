from scapy.all import *
from scapy.layers.dns import DNS, DNSRR
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether

import socket

DEVICE = "en0"
DNS_PORT = 53
DNS_IP = "127.0.0.3"


def get_domaine_ip(packet):
    if packet and packet.haslayer(DNS):
        name = packet[DNS].qd.qname  # Get the name from the DNS request packet
        name = name.decode("utf-8") # Convert the name from bytes to string
        name = name[:-1] # Remove the last character from the name
        ip_ans = dns_pool[name]  # Get the IP address from the DNS pool
        packet_handler(packet, name, ip_ans)


def packet_handler(packet, name, ip_ans):
    if ip_ans:
        print(f"Answering DNS request for {name} with {ip_ans}")
        
        eth = Ether(src=dhcpMac, dst=packet[Ether].src)
        ip = IP(src=DNS_IP, dst=packet[IP].src)
        udp = UDP(sport=DNS_PORT, dport=packet[UDP].sport)
        dns = DNS(id=packet[DNS].id, qr=1, qd=packet[DNS].qd, an=DNSRR(rrname=packet[DNS].qd.qname, ttl=10, rdata=ip_ans))
        packet_dns = eth / ip / udp / dns

        time.sleep(1)
        sendp(packet_dns, iface=DEVICE)
    else:
        print("Cant find the IP address for the requested name")

    time.sleep(1)
    
            
if __name__ == "__main__":
    dhcpMac = str(get_if_hwaddr(DEVICE))
    dns_pool = {'httpAPP': "127.0.0.4"}
    
    while True:
        print("Listening for DNS requests...")
        packet = sniff(iface=DEVICE, filter=f"udp and port {DNS_PORT}", count=1)[0]
        print("DNS request received")
        get_domaine_ip(packet)