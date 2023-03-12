import unittest
from dhcp import DHCP

class TestDHCP(unittest.TestCase):

    def setUp(self):
        self.dhcp = DHCP("192.168.0.1", "192.168.0.100-200")

    def test_constructor(self):
        self.assertEqual(self.dhcp.server_ip, "192.168.0.1")
        self.assertEqual(self.dhcp.ip_range, "192.168.0.100-200")

    def test_allocate_ip(self):
        ip_address = self.dhcp.allocate_ip("00:11:22:33:44:55")
        self.assertTrue(ip_address.startswith("192.168.0."))
        self.assertTrue(int(ip_address.split(".")[-1]) >= 100)
        self.assertTrue(int(ip_address.split(".")[-1]) <= 200)

    def test_release_ip(self):
        mac_address = "00:11:22:33:44:55"
        ip_address = self.dhcp.allocate_ip(mac_address)
        self.assertEqual(self.dhcp.release_ip(mac_address, ip_address), True)

if __name__ == '__main__':
    unittest.main()
