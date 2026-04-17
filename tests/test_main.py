from __future__ import print_function

import os
import sys
import unittest


# Ensure the repository root (containing main.py) is importable.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import main as wol_main


class _SilenceStdout(object):
    """File-like stdout for tests; accepts str and unicode (Python 2.7 safe).

    `io.StringIO` under Python 2 only accepts unicode, while
    `from __future__ import print_function` still passes byte `str` to
    `write()`, which raises TypeError. A no-op writer avoids that.
    """

    def write(self, data):
        pass

    def flush(self):
        pass


class FakeSocket(object):
    def __init__(self, *args, **kwargs):
        self.options = []
        self.sent = []
        self.closed = False

    def setsockopt(self, level, optname, value):
        self.options.append((level, optname, value))

    def sendto(self, data, addr):
        self.sent.append((data, addr))

    def close(self):
        self.closed = True


class SocketFactory(object):
    def __init__(self):
        self.instances = []

    def __call__(self, *args, **kwargs):
        inst = FakeSocket(*args, **kwargs)
        self.instances.append(inst)
        return inst


def _mac_to_bytes_for_assert(mac_address):
    mac = mac_address.replace(':', '').replace('-', '').upper()
    if len(mac) != 12:
        raise ValueError("Invalid MAC address format: {0}".format(mac_address))

    if sys.version_info[0] >= 3:
        return bytes.fromhex(mac)

    # Python 2.7: build a byte-string without bytes.fromhex().
    return ''.join(chr(int(mac[i:i + 2], 16)) for i in range(0, 12, 2))


class TestCreateMagicPacket(unittest.TestCase):
    def test_create_magic_packet_length_and_repetitions(self):
        mac = "c8:54:4b:41:40:1a"
        packet = wol_main.create_magic_packet(mac)

        # 6 bytes of 0xFF + 16 repetitions of 6 bytes MAC = 102 bytes total.
        self.assertEqual(len(packet), 102)
        self.assertEqual(packet[:6], b'\xff' * 6)

        expected_suffix = _mac_to_bytes_for_assert(mac) * 16
        self.assertEqual(packet[6:], expected_suffix)

    def test_create_magic_packet_accepts_dashes_and_case(self):
        mac = "aa-bb-cc-dd-ee-ff"
        packet = wol_main.create_magic_packet(mac)

        self.assertEqual(len(packet), 102)
        self.assertEqual(packet[:6], b'\xff' * 6)
        self.assertEqual(packet[6:], _mac_to_bytes_for_assert(mac) * 16)

    def test_create_magic_packet_invalid_mac_raises(self):
        with self.assertRaises(ValueError):
            wol_main.create_magic_packet("not-a-valid-mac")


class TestSendWoLPacket(unittest.TestCase):
    def setUp(self):
        self._orig_socket_ctor = wol_main.socket.socket
        self.factory = SocketFactory()
        wol_main.socket.socket = self.factory

    def tearDown(self):
        wol_main.socket.socket = self._orig_socket_ctor

    def test_send_wol_packet_success(self):
        old_stdout = sys.stdout
        sys.stdout = _SilenceStdout()
        mac = "c8:54:4b:41:40:1a"
        broadcast_ip = "192.168.0.255"
        port = 7

        try:
            ok = wol_main.send_wol_packet(mac, broadcast_ip=broadcast_ip, port=port)
            self.assertTrue(ok)
            self.assertEqual(len(self.factory.instances), 1)

            sock = self.factory.instances[0]
            self.assertTrue(sock.closed)
            self.assertIn(
                (wol_main.socket.SOL_SOCKET, wol_main.socket.SO_BROADCAST, 1),
                sock.options,
            )

            self.assertEqual(len(sock.sent), 1)
            sent_packet, addr = sock.sent[0]
            self.assertEqual(addr, (broadcast_ip, port))
            self.assertEqual(sent_packet, wol_main.create_magic_packet(mac))
        finally:
            sys.stdout = old_stdout

    def test_send_wol_packet_invalid_mac_returns_false(self):
        old_stdout = sys.stdout
        sys.stdout = _SilenceStdout()
        try:
            ok = wol_main.send_wol_packet("invalid-mac", broadcast_ip="192.168.0.255", port=9)
            self.assertFalse(ok)
            # Socket creation should not even happen if MAC parsing fails first.
            self.assertEqual(len(self.factory.instances), 0)
        finally:
            sys.stdout = old_stdout


class TestMain(unittest.TestCase):
    def setUp(self):
        self._orig_send_wol_packet = wol_main.send_wol_packet
        self.calls = []

        def fake_send_wol_packet(mac_address, broadcast_ip="255.255.255.255", port=9):
            self.calls.append((mac_address, broadcast_ip, port))
            return True

        wol_main.send_wol_packet = fake_send_wol_packet

    def tearDown(self):
        wol_main.send_wol_packet = self._orig_send_wol_packet

    def test_main_uses_provided_macs_and_flags(self):
        # Silence stdout during tests.
        old_stdout = sys.stdout
        sys.stdout = _SilenceStdout()
        try:
            wol_main.main(
                argv=[
                    "AA:BB:CC:DD:EE:FF",
                    "11:22:33:44:55:66",
                    "--broadcast-ip",
                    "1.2.3.4",
                    "--port",
                    "7",
                ]
            )
        finally:
            sys.stdout = old_stdout

        self.assertEqual(
            self.calls,
            [
                ("AA:BB:CC:DD:EE:FF", "1.2.3.4", 7),
                ("11:22:33:44:55:66", "1.2.3.4", 7),
            ],
        )

    def test_main_defaults_when_no_macs_given(self):
        old_stdout = sys.stdout
        sys.stdout = _SilenceStdout()
        try:
            wol_main.main(argv=[])
        finally:
            sys.stdout = old_stdout

        self.assertEqual(len(self.calls), len(wol_main.DEFAULT_MAC_ADDRESSES))
        for i, mac in enumerate(wol_main.DEFAULT_MAC_ADDRESSES):
            self.assertEqual(self.calls[i][0], mac)
            self.assertEqual(self.calls[i][1], "255.255.255.255")
            self.assertEqual(self.calls[i][2], 9)


if __name__ == "__main__":
    unittest.main()

