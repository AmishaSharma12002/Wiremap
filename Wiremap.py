# -*- coding: utf-8 -*-
"""Untitled16.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10vcTff4HajbL5o8G4Qb1sPZ1VvNiXBAL
"""

import sys
import argparse
import socket
from tqdm import tqdm
from scapy.all import *

def packet_handler(packet):
    # Process the received packet
    if packet.haslayer(IP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        print(f"Received IP packet from {src_ip} to {dst_ip}")
    elif packet.haslayer(TCP):
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
        print(f"Received TCP packet from {src_port} to {dst_port}")
    else:
        print("Received packet")

def sniff_packets(target_ip):
    # Sniff packets and call packet_handler for each packet
    sniff(filter=f"host {target_ip}", prn=packet_handler)

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Wiremap - Simple Port Scanner")

    # Add the command-line arguments
    parser.add_argument("-f", "--ip", required=True, help="Target IP address")
    parser.add_argument("-p", "--port", required=True, help="Port range (e.g., '1-100')")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the provided arguments
    target_ip = args.ip
    port_range = args.port.split("-")

    if len(port_range) != 2:
        print("Invalid port range. Please provide the range in the format 'start_port-end_port'.")
        sys.exit(1)

    start_port = int(port_range[0])
    end_port = int(port_range[1])

    # Validate the target IP address
    try:
        socket.inet_aton(target_ip)
    except socket.error:
        print("Invalid IP address")
        sys.exit(1)

    # Create a thread for packet sniffing
    sniffer_thread = threading.Thread(target=sniff_packets, args=(target_ip,))

    try:
        # Start the sniffer_thread
        sniffer_thread.start()

        # Start scanning the target IP for open ports
        open_ports = []

        print("Scanning ports...")

        # Use tqdm to display the progress bar
        with tqdm(total=end_port - start_port + 1, ncols=70) as pbar:
            for port in range(start_port, end_port + 1):
                # Create a socket to establish a TCP connection to the target IP and port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)  # Set a timeout value for the connection attempt

                # Try connecting to the target IP and port
                result = sock.connect_ex((target_ip, port))
                if result == 0:
                    open_ports.append(port)
                    print(f"Port {port} is open. Stopping port scanning.")
                    break

                sock.close()
                pbar.update(1)

        print("Scan completed.")

        # Display the results
        print("Open ports:")
        for port in open_ports:
            print(port)

    except KeyboardInterrupt:
        # Handle the keyboard interrupt gracefully
        print("\nWiremap interrupted by user")
        sys.exit(0)

    finally:
        # Wait for the sniffer_thread to complete
        sniffer_thread.join()

if __name__ == "__main__":
    main()
