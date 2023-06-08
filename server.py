import socket
import os
import hashlib

# UDP IP address and port number
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

# Packet size and buffer size
PACKET_SIZE = 1024
BUFFER_SIZE = 65535

#Create a file to receive data
filename = "received_file.txt" 
with open(filename, "w") as file:
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the IP address and port number
    server_socket.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

    # Initialize the expected sequence number
    expected_sequence_number = 0

    while True:
        # Receive a packet from the client
        packet, client_address = server_socket.recvfrom(BUFFER_SIZE)

        # Extract the header, checksum, and payload from the packet
        header = packet[:4].decode('utf-8')
        checksum = packet[4:36].decode('utf-8')
        payload = packet[36:]

        # Verify the checksum
        if hashlib.md5(payload).hexdigest() != checksum:
            # If the checksum is incorrect, request the sender to resend the packet
            print("Check sum no is incorrect, request resend ")
            server_socket.sendto(header.encode('utf-8'), client_address)
            continue

        # Check if the sequence number is as expected
        if int(header) != expected_sequence_number:
            # If the sequence number is incorrect, request the sender to resend the packet
            print("Sequence no is incorrect, request resend ")
            server_socket.sendto(header.encode('utf-8'), client_address)
            continue

        # Write the payload to the file
        print(f"Payload : {payload.decode('utf-8')}")
        payload = packet[36:].decode('utf-8')
        file.write(payload)

        # Send ACK message to the client
        server_socket.sendto(header.encode('utf-8'), client_address)

        # Increment the expected sequence number
        expected_sequence_number += 1

        # If an empty packet is received, the file transfer is complete
        if not payload:
            print("File has received completely")
            break

    # Close the socket
    server_socket.close()

    # Print the size of the received file
    received_file_size = os.path.getsize(filename)
    print(f"Received file size: {received_file_size} bytes")
