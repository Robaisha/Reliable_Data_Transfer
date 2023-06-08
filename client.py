import socket
import os
import hashlib

# UDP IP address and port number
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

# Packet size and buffer size
PACKET_SIZE = 1024
BUFFER_SIZE = 65535

# Timeout for receiving ACK message
TIMEOUT = 1.0

#Open file to send
filename = "file.txt"  # Replace with the name of the file you want to send
file_size = os.path.getsize(filename)
print(f"File size : {file_size}")

# Initialize the sequence number, packet count, and window size
sequence_number = 0
packet_count = 0
packets = []
window_size = 1
# Set the maximum window size
max_window_size = 5 

with open(filename, "rb") as file:
    #Socket creation and set the timeout
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)

    #Loop to Send the file in packets
    while True:
        # Check if the window is full
        if packet_count - sequence_number >= window_size:
            try:
                # Wait for ACK message from the server to move the window forward
                ack, server_address = client_socket.recvfrom(BUFFER_SIZE)
                ack_number = int(ack.decode('utf-8'))
                print(f"Acknowledgement : {ack_number}")
                if ack_number >= sequence_number:
                    # Update the window size dynamically based on the ACK received
                    window_size = min(max_window_size, ack_number - sequence_number + 1)
                    sequence_number = ack_number + 1
                    print(f"Sequence No : {sequence_number}")
            except socket.timeout:
                # Timeout occurred, resend the packets in the current window
                print("Timeout occurred, resending packets in the current window")
                for i in range(sequence_number, packet_count):
                    client_socket.sendto(packets[i], (UDP_IP_ADDRESS, UDP_PORT_NO))

        # Read a chunk of data from the file
        data = file.read(PACKET_SIZE)
        if not data:
            break

        # Create the packet with header and payload
        header = str(packet_count).zfill(4)
        checksum = hashlib.md5(data).hexdigest()
        packet = header + checksum + data.decode('utf-8')

        # Send the packet to the receiver and add it to the window
        client_socket.sendto(packet.encode('utf-8'), (UDP_IP_ADDRESS, UDP_PORT_NO))
        packets.append(packet)

        # Increment the packet count
        packet_count += 1
        print(f"Packet No  {packet_count}")

    # Wait for all packets to be acknowledged
    while sequence_number < packet_count:
        try:
            # Wait for ACK message from the receiver to move the window forward
            ack, server_address = client_socket.recvfrom(BUFFER_SIZE)
            ack_number = int(ack.decode('utf-8'))
            print(f"Acknowledgement : {ack_number}")
            if ack_number >= sequence_number:
                # Update the window size dynamically based on the ACK received
                window_size = min(max_window_size, ack_number - sequence_number + 1)
                sequence_number = ack_number + 1
                print(f"Sequence No : {sequence_number}")
        except socket.timeout:
            # Timeout occurred, resend the packets in the current window
            print("Timeout occurred, resending packets in the current window")
            for i in range(sequence_number, packet_count):
                client_socket.sendto(packets[i], (UDP_IP_ADDRESS, UDP_PORT_NO))

    #Empty Packet to show end of file
    header = str(packet_count).zfill(4)
    checksum = hashlib.md5(b"").hexdigest()
    packet = header + checksum
    client_socket.sendto(packet.encode('utf-8'), (UDP_IP_ADDRESS, UDP_PORT_NO))

    # Print the number of packets sent
    print(f"Sent {packet_count} packets")

    # Close the socket
    client_socket.close()
