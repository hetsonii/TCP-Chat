import socket
import threading
import os
import signal
import sys
from termcolor import colored
from colorama import init
from pyfiglet import figlet_format

clients = []  

def caesar_cipher(text, shift):
    result = ''
    for char in text:
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - start + shift) % 26 + start)
        else:
            result += char
    return result

def handle_client(client_socket, addr):
    client_socket.send("Enter Caesar Cipher Shift (integer): ".encode('utf-8'))
    shift_data = client_socket.recv(1024).decode('utf-8')
    shift = int(shift_data)

    client_socket.send("Enter your name: ".encode('utf-8'))
    name = client_socket.recv(1024).decode('utf-8')

    print(colored(f"{name} has joined with shift value: {shift}", 'green'))

    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        decoded_data = data.decode('utf-8')
        print(f"\nReceived from {addr} [{name}]: {decoded_data}")

        if decoded_data.lower() == "/disconnect":
            print(f"[*] {addr} [{name}] has disconnected.")
            break

        # Apply the Caesar cipher to the received message
        encoded_data = caesar_cipher(decoded_data, shift)

        # Print the encoded (ciphered) message on the server side
        print(f"Encoded message from {name}: {encoded_data}")

        # Broadcast the encoded (ciphered) message to all other clients
        broadcast(f"{name}: {encoded_data}".encode('utf-8'), client_socket)

    client_socket.close()


def broadcast(message, sender_socket):
    global clients

    for client in clients:
        try:
            if client != sender_socket:
                client.send(message)
        except Exception as e:
            print(colored(f"Error broadcasting message to a client: {e}", 'red'))


def print_banner():
    banner = figlet_format("Chat Server", font="slant")
    print(colored(banner, 'green'))


def main():
    if len(sys.argv) != 3:
        print("Usage: python server.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    print_banner()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((host, port))
    except OSError as e:
        print(colored(f"Error binding to {host}:{port}: {e}", 'red'))

        try:
            process_pid = os.popen(f"lsof -t -i:{port}").read().strip()
            if process_pid:
                os.kill(int(process_pid), signal.SIGTERM)
                print(colored(f"Terminated the process using port {port}.", 'yellow'))
            else:
                print(colored(f"No process found using port {port}.", 'yellow'))
        except Exception as e:
            print(colored(f"Error terminating process: {e}", 'red'))

        return

    server_socket.listen(5)

    print(colored(f"[*] Listening on {host}:{port}", 'green'))

    while True:
        client_socket, addr = server_socket.accept()
        print(colored(f"[*] Accepted connection from {addr[0]}:{addr[1]}", 'green'))

        clients.append(client_socket)

        # Inform other clients about the new connection (no 'name' available at this point)
        message = f"[*] {addr[0]}:{addr[1]} has joined the chat. Total number of clients: {len(clients)}"
        broadcast(message.encode('utf-8'), client_socket)

        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    main()