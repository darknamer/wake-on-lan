#!/usr/bin/env python
"""
Wake-on-LAN script to wake devices with specific MAC addresses.
"""

from __future__ import print_function

import argparse
import socket
import sys


DEFAULT_MAC_ADDRESSES = [
    "c8:54:4b:41:40:1a",
    # Add more MAC addresses here as needed
    # "aa:bb:cc:dd:ee:ff",
    "d4:5d:64:25:a7:60",  # darknamer pc
]


def create_magic_packet(mac_address):
    """
    Create a magic packet for Wake-on-LAN.
    
    Args:
        mac_address: MAC address in format 'XX:XX:XX:XX:XX:XX'
    
    Returns:
        Magic packet as bytes (as `str` under Python 2.7)
    """
    # Remove any separators and convert to uppercase
    mac = mac_address.replace(':', '').replace('-', '').upper()
    
    # Validate MAC address format
    if len(mac) != 12:
        raise ValueError("Invalid MAC address format: {0}".format(mac_address))
    
    # Convert MAC address to bytes.
    # Python 2.7 does not have `bytes.fromhex`.
    if sys.version_info[0] >= 3:
        mac_bytes = bytes.fromhex(mac)
    else:
        mac_bytes = ''.join(chr(int(mac[i:i + 2], 16)) for i in range(0, 12, 2))
    
    # Create magic packet: 6 bytes of 0xFF followed by 16 repetitions of MAC address
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    
    return magic_packet


def send_wol_packet(mac_address, broadcast_ip='255.255.255.255', port=9):
    """
    Send Wake-on-LAN magic packet to wake a device.
    
    Args:
        mac_address: MAC address in format 'XX:XX:XX:XX:XX:XX'
        broadcast_ip: Broadcast IP address (default: 255.255.255.255)
        port: Port to send packet on (default: 9, alternative: 7)
    
    Returns:
        True if packet was sent successfully, False otherwise
    """
    try:
        # Create magic packet
        magic_packet = create_magic_packet(mac_address)
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Send magic packet
        sock.sendto(magic_packet, (broadcast_ip, port))
        sock.close()
        
        print("Wake-on-LAN packet sent successfully to {0}".format(mac_address))
        return True
        
    except Exception as e:
        print("Error sending Wake-on-LAN packet: {0}".format(e))
        return False


def main(argv=None):
    """Main function to wake devices."""
    if argv is None:
        argv = sys.argv[1:]

    epilog = (
        "Examples:\n"
        "  python main.py AA:BB:CC:DD:EE:FF\n"
        "  python main.py AA:BB:CC:DD:EE:FF 11:22:33:44:55:66\n"
        "  python main.py AA:BB:CC:DD:EE:FF --broadcast-ip 192.168.1.255 --port 9\n"
        "\n"
        "MACs should be provided as: XX:XX:XX:XX:XX:XX"
    )
    parser = argparse.ArgumentParser(
        description='Send Wake-on-LAN magic packets to devices by MAC address.',
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    parser.add_argument(
        '-h',
        '--help',
        action='help',
        help='show this help message and exit',
    )
    parser.add_argument(
        'mac_addresses',
        nargs='*',
        help="One or more MAC addresses (format: XX:XX:XX:XX:XX:XX). If omitted, uses defaults in code.",
    )
    parser.add_argument(
        '--broadcast-ip',
        dest='broadcast_ip',
        default='255.255.255.255',
        help='Broadcast IP address to send to (default: 255.255.255.255)',
    )
    parser.add_argument(
        '--port',
        dest='port',
        type=int,
        default=9,
        help='UDP port to send to (default: 9)',
    )

    args = parser.parse_args(argv)
    mac_addresses = args.mac_addresses if args.mac_addresses else DEFAULT_MAC_ADDRESSES
    
    print("-" * 50)
    print("Attempting to wake {0} device(s)...".format(len(mac_addresses)))
    print("-" * 50)
    
    for mac_address in mac_addresses:
        print("Waking device with MAC address: {0}".format(mac_address))
        send_wol_packet(mac_address, broadcast_ip=args.broadcast_ip, port=args.port)
        print()
    
    print("-" * 50)
    print("Wake-on-LAN process completed.")
    print("-" * 50)


if __name__ == "__main__":
    main()
