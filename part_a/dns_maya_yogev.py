from scapy.all import *
from scapy.layers.dns import DNS, DNSRR
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
import sys
import signal
import dns.resolver
import socket

DEVICE = "en0"
DNS_PORT = 53
DNS_IP = "127.0.0.3"


def get_domaine_ip(packet):
    try:
        if not packet or not packet.haslayer(DNS):
            return
        name = packet[DNS].qd.qname.decode("utf-8")[:-1]
        ip_ans = dns_ip_pool.get(name)
        if not ip_ans:
            print(f"{name} not found in local DNS cache. Querying Google DNS...")
            answers = dns.resolver.query(name)
            for rdata in answers:
                ip_ans = str(rdata)
                break
            dns_ip_pool[name] = ip_ans
        packet_handler(packet, name, ip_ans)
    except Exception as e:
        print(f"An error occurred while processing DNS request: {e}")




def packet_handler(packet, name, ip_ans):
    try:
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
            raise ValueError("IP address not found for requested name")

    except ValueError as e:
        print(str(e))

    time.sleep(1)



def signal_handler(sig, frame):
    print('Exiting...')
    sys.exit(0)
    
    
    
    
            
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    dhcpMac = str(get_if_hwaddr(DEVICE))
    dns_ip_pool = {"httpAPP": "127.0.0.1", "google.com" : "8.8.8.8", "facebook.com" : "1.2.3.4"}

    def listen_for_dns_requests():
        try:
            print("Listening for DNS requests...")
            packet = sniff(iface=DEVICE, filter=f"udp and port {DNS_PORT}", count=1)[0]
            print("DNS request received")
            get_domaine_ip(packet)
        except KeyboardInterrupt:
            print("Stopping DNS server...")
            sys.exit(0)
        except Exception as e:
            print(f"An error occurred while listening for DNS requests: {e}")

    try:
        while True:
            listen_for_dns_requests()
    except KeyboardInterrupt:
        print("Stopping DNS server...")
        sys.exit(0)
