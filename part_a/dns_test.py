import unittest
from unittest.mock import patch, MagicMock
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, UDP, TCP

from dns import get_domaine_ip, packet_handler


class TestDns(unittest.TestCase):

    def setUp(self):
        self.packet = IP(dst="8.8.8.8") / UDP() / DNS(rd=1, qd=DNSQR(qname="www.example.com"))

    @patch("dns.dns_pool", {"www.example.com": "127.0.0.1"})
    def test_get_domaine_ip_with_valid_packet(self):
        # Test that get_domaine_ip correctly handles a DNS packet with a valid domain name
        # and IP address in the dns_pool
        with patch("dns.packet_handler") as mock_handler:
            get_domaine_ip(self.packet)
            mock_handler.assert_called_once_with(self.packet, "www.example.com", "127.0.0.1")

    def test_get_domaine_ip_with_invalid_packet(self):
        # Test that get_domaine_ip does not call packet_handler with an invalid packet
        invalid_packet = IP(dst="8.8.8.8") / TCP()
        with patch("dns.packet_handler") as mock_handler:
            get_domaine_ip(invalid_packet)
            mock_handler.assert_not_called()

    @patch("dns.dns_pool", {"www.example.com": None})
    def test_get_domaine_ip_with_no_ip_address(self):
        # Test that get_domaine_ip correctly handles a DNS packet with a valid domain name
        # but no IP address in the dns_pool
        with patch("dns.packet_handler") as mock_handler:
            get_domaine_ip(self.packet)
            mock_handler.assert_called_once_with(self.packet, "www.example.com", None)

    @patch("dns.sendp")
    def test_packet_handler_with_valid_ip_address(self, mock_sendp):
        # Test that packet_handler correctly constructs a DNS response packet with a valid
        # IP address and sends it using sendp
        packet = IP() / UDP() / DNS()
        name = "www.example.com"
        ip_ans = "127.0.0.1"
        dhcpMac = "00:11:22:33:44:55"
        with patch("dns.time.sleep"):
            packet_handler(packet, name, ip_ans, dhcpMac)
            mock_sendp.assert_called_once_with(packet, iface="en0")

    def test_packet_handler_with_no_ip_address(self):
        # Test that packet_handler correctly prints a message when no IP address is found
        # for the requested domain name
        packet = IP() / UDP() / DNS()
        name = "www.example.com"
        ip_ans = None
        dhcpMac = "00:11:22:33:44:55"
        with patch("dns.time.sleep"), patch("builtins.print") as mock_print:
            packet_handler(packet, name, ip_ans, dhcpMac)
            mock_print.assert_called_once_with("Cant find the IP address for the requested name")
