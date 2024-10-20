import socket
import threading
import sys
from termcolor import colored
from colorama import init
from pyfiglet import figlet_format

def receive_messages(client_socket):
    try:
        while True:
            # Receive and print the encoded message from the server
            encoded_message = client_socket.recv(1024).decode('utf-8')
            print(f"{encoded_message}")
    except Exception as e:
        print(f"Error receiving messages: {e}")
    finally:
        client_socket.close()
        exit(0)

def print_banner():
    banner = figlet_format("Chat Client", font="slant")
    print(colored(banner, 'green'))

def main():
    # Parse command line arguments for host and port
    if len(sys.argv) != 3:
        print(colored("Usage: python client.py <host> <port>", 'red'))
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    print_banner()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Receive and print the prompt to enter shift
    shift_prompt = client_socket.recv(1024).decode('utf-8')
    print(shift_prompt, end=' ')

    # Set the Caesar Cipher shift
    shift = int(input())

    # Send the shift to the server
    client_socket.send(str(shift).encode('utf-8'))

    # Receive and print the prompt to enter name
    name_prompt = client_socket.recv(1024).decode('utf-8')
    print(name_prompt, end=' ')

    # Set the name
    name = input()

    # Send the name to the server
    client_socket.send(name.encode('utf-8'))

    # Start a thread to receive messages from the server
    message_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    message_thread.start()

    try:
        while True:
            message = input("Enter a message (or type '/disconnect' to exit): ")
            client_socket.send(message.encode('utf-8'))

            if message.lower() == "/disconnect":
                break

    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
